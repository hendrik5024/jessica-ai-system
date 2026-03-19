import os
import json
from dataclasses import dataclass

import datasets
from datasets import load_dataset
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model, PeftModel

# Simple instruction dataset loader for our JSONL format

def load_jsonl_dataset(path: str):
    return load_dataset("json", data_files={"train": path})


def format_example(example, tokenizer, max_len=512):
    instr = example.get("instruction", "")
    inp = example.get("input", "")
    out = example.get("output", "")
    text = f"### Instruction:\n{instr}\n\n### Input:\n{inp}\n\n### Response:\n{out}"
    return tokenizer(text, truncation=True, max_length=max_len, padding="max_length")


@dataclass
class TrainArgs:
    base_model: str
    data_path: str
    output_dir: str
    model_type: str = "chat"  # "chat" or "code"
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lr: float = 1e-4
    epochs: int = 2
    batch_size: int = 8
    grad_accum: int = 4
    max_seq_len: int = 512
    warmup_ratio: float = 0.1


def train(args: TrainArgs):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[train_lora] Using device: {device}, model_type: {args.model_type}")
    
    tokenizer = AutoTokenizer.from_pretrained(args.base_model, use_fast=True)
    tokenizer.pad_token = tokenizer.eos_token
    
    dtype = torch.float16 if device == "cuda" else torch.float32
    model = AutoModelForCausalLM.from_pretrained(
        args.base_model, 
        torch_dtype=dtype,
        device_map="auto" if device == "cuda" else None
    )
    if device != "cuda":
        model.to(device)

    ds = load_jsonl_dataset(args.data_path)
    ds = ds.map(
        lambda e: format_example(e, tokenizer, args.max_seq_len), 
        batched=False
    )

    lconf = LoraConfig(
        r=args.lora_r, 
        lora_alpha=args.lora_alpha, 
        lora_dropout=args.lora_dropout, 
        target_modules=["q_proj", "v_proj"],
        task_type="CAUSAL_LM",
        bias="none"
    )
    peft_model = get_peft_model(model, lconf)
    peft_model.print_trainable_parameters()

    optimizer = torch.optim.AdamW(peft_model.parameters(), lr=args.lr)
    total_steps = (len(ds["train"]) // (args.batch_size * args.grad_accum)) * args.epochs
    warmup_steps = int(total_steps * args.warmup_ratio)
    scheduler = torch.optim.lr_scheduler.get_linear_schedule_with_warmup(
        optimizer, warmup_steps, total_steps
    )

    peft_model.train()
    os.makedirs(args.output_dir, exist_ok=True)

    step = 0
    accumulated_loss = 0.0
    for epoch in range(args.epochs):
        for i in range(len(ds["train"])):
            batch = ds["train"][i]
            input_ids = torch.tensor([batch["input_ids"]], device=device)
            attention_mask = torch.tensor([batch["attention_mask"]], device=device)
            labels = input_ids.clone()

            out = peft_model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = out.loss / args.grad_accum
            loss.backward()
            accumulated_loss += loss.item()

            if (i + 1) % args.grad_accum == 0:
                torch.nn.utils.clip_grad_norm_(peft_model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad()
                step += 1
                if step % 50 == 0:
                    print(f"epoch={epoch+1} step={step} loss={accumulated_loss:.4f} lr={scheduler.get_last_lr()[0]:.2e}")
                accumulated_loss = 0.0

    peft_model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print(f"[train_lora] Saved {args.model_type} adapter to {args.output_dir}")


if __name__ == "__main__":
    base_model = os.environ.get("JESSICA_BASE_HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.3")
    data_path = os.environ.get("JESSICA_DATASET", "datasets/user_finetune/train.jsonl")
    out_dir = os.environ.get("JESSICA_LORA_OUT", "adapters/chat/latest")
    model_type = os.environ.get("JESSICA_MODEL_TYPE", "chat")

    args = TrainArgs(
        base_model=base_model, 
        data_path=data_path, 
        output_dir=out_dir,
        model_type=model_type
    )
    train(args)
