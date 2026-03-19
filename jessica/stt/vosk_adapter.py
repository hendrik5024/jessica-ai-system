# Basic wrapper. If Vosk not installed or model missing, returns explanatory error.
def transcribe_from_wav(path: str, timeout: int = 30) -> str:
    try:
        from vosk import Model, KaldiRecognizer  # type: ignore
        import wave, json
    except Exception:
        return "[STT unavailable: vosk not installed or environment missing]"

    try:
        wf = wave.open(path, "rb")
    except Exception as e:
        return f"[STT error opening file: {e}]"

    try:
        model = Model("vosk-model")  # user must place model folder here
        rec = KaldiRecognizer(model, wf.getframerate())
        results = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                res = rec.Result()
                results.append(json.loads(res).get("text", ""))
        results.append(json.loads(rec.FinalResult()).get("text", ""))
        return " ".join([r for r in results if r])
    except Exception as e:
        return f"[STT runtime error: {e}]"
