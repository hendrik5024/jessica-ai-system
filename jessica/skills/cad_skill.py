"""
Jessica CAD Design Skill - 3D CAD generation with CadQuery.

Provides parametric CAD design capabilities:
- Generate 3D parts (boxes, brackets, custom shapes)
- Center holes and other features
- Export to STL for 3D printing
- Validate watertightness with Trimesh
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
from datetime import datetime

try:
    import cadquery as cq
except ImportError:
    raise ImportError("cadquery not installed. Install with: pip install cadquery")

try:
    import trimesh
except ImportError:
    raise ImportError("trimesh not installed. Install with: pip install trimesh")

logger = logging.getLogger("jessica.cad")


class JessicaCAD:
    """
    CAD design system for parametric part generation.
    
    Capabilities:
    - Parametric box creation with holes
    - Bracket design
    - Feature-based modeling
    - STL export for 3D printing
    - Mesh validation (watertightness check)
    """
    
    def __init__(self, output_dir: str = "./cad_output"):
        """
        Initialize CAD system.
        
        Args:
            output_dir: Directory to save generated STL files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.last_generated_file: Optional[str] = None
        self.generation_history: list = []
        
        logger.info(f"JessicaCAD initialized. Output directory: {self.output_dir}")
    
    def generate_parametric_part(
        self,
        length: float,
        width: float,
        height: float,
        hole_diameter: float = 0,
        hole_depth: Optional[float] = None,
        hole_offset_x: float = 0,
        hole_offset_y: float = 0,
        part_name: str = "parametric_part"
    ) -> Dict[str, Any]:
        """
        Generate a parametric 3D box with optional center hole.
        
        Creates a rectangular prism with configurable dimensions and
        an optional drilled hole (useful for brackets, mounting blocks, etc).
        
        Args:
            length: X dimension in mm
            width: Y dimension in mm
            height: Z dimension in mm
            hole_diameter: Hole diameter in mm (0 = no hole)
            hole_depth: Hole depth in mm (None = through hole)
            hole_offset_x: Hole offset from center in X (mm)
            hole_offset_y: Hole offset from center in Y (mm)
            part_name: Name for the part (used in filename)
        
        Returns:
            Dict with:
            - 'success': True if generated
            - 'file_path': Path to generated STL
            - 'dimensions': (length, width, height)
            - 'hole_diameter': Hole diameter
            - 'file_size_mb': Size of STL file
            - 'timestamp': Generation timestamp
            - 'part_name': Name of part
        """
        try:
            # Validate inputs
            if length <= 0 or width <= 0 or height <= 0:
                return {
                    'success': False,
                    'error': f'Dimensions must be positive. Got: {length}x{width}x{height}'
                }
            
            if hole_diameter < 0:
                return {
                    'success': False,
                    'error': f'Hole diameter must be non-negative. Got: {hole_diameter}'
                }
            
            logger.info(f"Generating part: {part_name} ({length}x{width}x{height}mm, hole={hole_diameter}mm)")
            
            # Create base box
            box = cq.Workplane("XY").box(length, width, height)
            
            # Add hole if specified
            if hole_diameter > 0:
                # Use hole_depth or default to through hole
                hole_d = hole_depth if hole_depth is not None else height + 1  # +1 to ensure through
                
                # Drill hole from top surface at specified offset
                box = (box
                    .faces(">Z")
                    .workplane()
                    .pushPoints([(hole_offset_x, hole_offset_y)])
                    .hole(hole_diameter, hole_d)
                )
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{part_name}_{timestamp}.stl"
            filepath = self.output_dir / filename
            
            # Export to STL
            cq.exporters.export(box, str(filepath))
            
            # Get file size
            file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
            
            result = {
                'success': True,
                'file_path': str(filepath),
                'filename': filename,
                'dimensions': (length, width, height),
                'hole_diameter': hole_diameter,
                'hole_depth': hole_depth,
                'file_size_mb': round(file_size_mb, 3),
                'timestamp': timestamp,
                'part_name': part_name
            }
            
            # Store in history
            self.last_generated_file = str(filepath)
            self.generation_history.append(result)
            
            logger.info(f"Generated part: {filepath} ({file_size_mb:.3f} MB)")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate part: {e}")
            return {
                'success': False,
                'error': f'CAD generation failed: {str(e)}'
            }
    
    def generate_bracket(
        self,
        length: float,
        width: float,
        height: float,
        hole_diameter: float,
        chamfer_radius: float = 0.5,
        part_name: str = "bracket"
    ) -> Dict[str, Any]:
        """
        Generate a bracket with mounting hole.
        
        Convenience function for creating brackets specifically.
        
        Args:
            length: X dimension in mm
            width: Y dimension in mm
            height: Z dimension in mm
            hole_diameter: Center hole diameter in mm
            chamfer_radius: Edge chamfer radius in mm
            part_name: Name for the part
        
        Returns:
            Generation result dict
        """
        try:
            # Create box
            bracket = cq.Workplane("XY").box(length, width, height)
            
            # Add chamfers for finished look
            bracket = bracket.edges("|Z").chamfer(chamfer_radius)
            
            # Add center hole
            bracket = bracket.faces(">Z").workplane().hole(hole_diameter, height)
            
            # Export
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{part_name}_{timestamp}.stl"
            filepath = self.output_dir / filename
            
            cq.exporters.export(bracket, str(filepath))
            
            file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
            
            result = {
                'success': True,
                'file_path': str(filepath),
                'filename': filename,
                'type': 'bracket',
                'dimensions': (length, width, height),
                'hole_diameter': hole_diameter,
                'chamfer_radius': chamfer_radius,
                'file_size_mb': round(file_size_mb, 3),
                'timestamp': timestamp,
                'part_name': part_name
            }
            
            self.last_generated_file = str(filepath)
            self.generation_history.append(result)
            
            logger.info(f"Generated bracket: {filepath}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate bracket: {e}")
            return {
                'success': False,
                'error': f'Bracket generation failed: {str(e)}'
            }
    
    def validate_stl_watertight(self, stl_path: str) -> Dict[str, Any]:
        """
        Validate if an STL file is watertight and ready for 3D printing.
        
        Uses Trimesh to check mesh integrity:
        - Watertight check
        - Face and vertex count
        - Volume calculation
        - Manifold check
        
        Args:
            stl_path: Path to STL file
        
        Returns:
            Dict with:
            - 'success': True if file is valid
            - 'is_watertight': Whether mesh is watertight
            - 'is_manifold': Whether mesh is manifold
            - 'face_count': Number of faces
            - 'vertex_count': Number of vertices
            - 'volume_cm3': Volume in cubic centimeters
            - 'surface_area_cm2': Surface area in square centimeters
            - 'warnings': Any issues found
            - 'ready_for_print': Overall assessment
        """
        try:
            # Load mesh
            mesh = trimesh.load(stl_path)
            
            logger.info(f"Validating STL: {stl_path}")
            
            warnings = []
            
            # Check watertightness
            is_watertight = mesh.is_watertight
            if not is_watertight:
                warnings.append("Mesh is NOT watertight - may have print issues")
            
            # Check if manifold
            is_manifold = mesh.is_watertight  # Watertight implies manifold
            
            # Get statistics
            face_count = len(mesh.faces)
            vertex_count = len(mesh.vertices)
            volume_cm3 = abs(mesh.volume) / 1000  # Convert mm^3 to cm^3
            surface_area_cm2 = mesh.area / 100  # Convert mm^2 to cm^2
            
            # Warnings for edge cases
            if face_count < 4:
                warnings.append(f"Very few faces ({face_count}) - likely degenerate mesh")
            
            if vertex_count < 4:
                warnings.append(f"Very few vertices ({vertex_count}) - likely degenerate mesh")
            
            if volume_cm3 <= 0:
                warnings.append("Zero or negative volume - invalid part")
            
            # Overall assessment
            ready_for_print = is_watertight and volume_cm3 > 0 and not warnings
            
            result = {
                'success': True,
                'file_path': stl_path,
                'is_watertight': is_watertight,
                'is_manifold': is_manifold,
                'face_count': int(face_count),
                'vertex_count': int(vertex_count),
                'volume_cm3': round(volume_cm3, 3),
                'surface_area_cm2': round(surface_area_cm2, 3),
                'warnings': warnings,
                'ready_for_print': ready_for_print,
                'print_recommendation': (
                    "Ready for printing!" if ready_for_print
                    else "Review issues before printing"
                )
            }
            
            logger.info(f"Validation result: watertight={is_watertight}, volume={volume_cm3:.3f}cm3")
            
            return result
            
        except FileNotFoundError:
            return {
                'success': False,
                'error': f'File not found: {stl_path}'
            }
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return {
                'success': False,
                'error': f'Validation failed: {str(e)}'
            }
    
    def validate_last_generated(self) -> Dict[str, Any]:
        """Validate the last generated file"""
        if not self.last_generated_file:
            return {
                'success': False,
                'error': 'No file has been generated yet'
            }
        
        return self.validate_stl_watertight(self.last_generated_file)
    
    def get_generation_history(self, limit: int = 10) -> list:
        """Get recent generation history"""
        return self.generation_history[-limit:]
    
    def clear_output_directory(self) -> Dict[str, Any]:
        """Delete all generated STL files"""
        try:
            import shutil
            count = 0
            for stl_file in self.output_dir.glob("*.stl"):
                stl_file.unlink()
                count += 1
            
            logger.info(f"Cleared {count} STL files from output directory")
            
            return {
                'success': True,
                'files_deleted': count,
                'directory': str(self.output_dir)
            }
        except Exception as e:
            logger.error(f"Failed to clear directory: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
_cad_system = None


def get_jessica_cad(output_dir: str = "./cad_output") -> JessicaCAD:
    """Get or create JessicaCAD singleton"""
    global _cad_system
    if _cad_system is None:
        _cad_system = JessicaCAD(output_dir)
    return _cad_system
