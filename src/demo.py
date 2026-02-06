"""
Map Declutter Demo
Demonstrates the AI-powered map decluttering algorithm
"""

from map_engine import BoundingBox, MapElement, MapDeclutterEngine
from visualizer import MapVisualizer


def create_demo_map():
    """
    Create a demo map with intentional overlaps
    
    Scenario: A city map with roads, a river, and overlapping labels/icons
    """
    elements = []
    
    # === FIXED ELEMENTS (High Priority - Never Move) ===
    
    # Road 1 (Horizontal)
    elements.append(MapElement(
        id="road_1",
        element_type="road",
        bbox=BoundingBox(20, 80, 160, 15)
    ))
    
    # Road 2 (Vertical)
    elements.append(MapElement(
        id="road_2",
        element_type="road",
        bbox=BoundingBox(95, 20, 15, 160)
    ))
    
    # River (Diagonal)
    elements.append(MapElement(
        id="river_1",
        element_type="river",
        bbox=BoundingBox(130, 100, 60, 12)
    ))
    
    # === MOVABLE ELEMENTS (Low Priority - Can Move) ===
    
    # Labels that overlap with roads/river
    elements.append(MapElement(
        id="L1",
        element_type="label",
        bbox=BoundingBox(30, 83, 25, 12)  # Overlaps road_1 (easier to move)
    ))
    
    elements.append(MapElement(
        id="L2",
        element_type="label",
        bbox=BoundingBox(98, 140, 25, 12)  # Overlaps road_2
    ))
    
    elements.append(MapElement(
        id="L3",
        element_type="label",
        bbox=BoundingBox(135, 102, 25, 10)   # Overlaps river_1
    ))
    
    # Icons that overlap
    elements.append(MapElement(
        id="I1",
        element_type="icon",
        bbox=BoundingBox(100, 50, 12, 12)  # Overlaps road_2
    ))
    
    elements.append(MapElement(
        id="I2",
        element_type="icon",
        bbox=BoundingBox(160, 103, 12, 10) # Overlaps river_1
    ))
    
    return elements


def print_algorithm_steps(engine):
    """Print step-by-step algorithm explanation"""
    print("\n" + "="*70)
    print("🔍 ALGORITHM EXECUTION STEPS")
    print("="*70)
    
    print("\n1️⃣ ELEMENT CLASSIFICATION:")
    print(f"   • Fixed elements (roads, rivers): {len(engine.fixed_elements)}")
    print(f"   • Movable elements (labels, icons): {len(engine.movable_elements)}")
    
    print("\n2️⃣ OVERLAP DETECTION:")
    for movable in engine.movable_elements:
        overlaps = [e for e in engine.find_overlaps(movable) if not e.movable]
        if overlaps:
            overlap_names = ', '.join([e.id for e in overlaps])
            print(f"   • {movable.id} overlaps with: {overlap_names}")
    
    print("\n3️⃣ RUNNING RESOLUTION ALGORITHM...")
    iterations = engine.resolve_clutter()
    print(f"   • Completed in {iterations} iterations")
    
    print("\n4️⃣ REPOSITIONING RESULTS:")
    for movable in engine.movable_elements:
        if movable.moved:
            dx = movable.bbox.x - movable.original_bbox.x
            dy = movable.bbox.y - movable.original_bbox.y
            print(f"   • {movable.id}: moved ({dx:+.0f}, {dy:+.0f}) pixels")
        else:
            print(f"   • {movable.id}: no movement needed")


def main():
    """Main demo execution with error handling"""
    try:
        print("\n" + "="*70)
        print("MAP DECLUTTER AI - HACKATHON DEMO")
        print("="*70)
        
        # Create demo map
        print("\n[*] Creating demo map with intentional overlaps...")
        elements = create_demo_map()
        if not elements:
            raise ValueError("Failed to create demo map elements")
        print(f"[OK] Created {len(elements)} map elements")
        
        # Initialize engine
        print("\n[*] Initializing declutter engine...")
        engine = MapDeclutterEngine(elements)
        if not engine:
            raise ValueError("Failed to initialize declutter engine")
        
        # Show algorithm execution
        print_algorithm_steps(engine)
        
        # Get statistics
        stats = engine.get_statistics()
        if not stats:
            raise ValueError("Failed to generate statistics")
        
        print("\n" + "="*70)
        print("FINAL STATISTICS")
        print("="*70)
        print(f"Total elements:       {stats['total_elements']}")
        print(f"Fixed elements:       {stats['fixed_elements']}")
        print(f"Movable elements:     {stats['movable_elements']}")
        print(f"Elements moved:       {stats['elements_moved']}")
        print(f"Success rate:         {stats['move_percentage']:.1f}%")
        print("="*70)
        
        # Visualize results
        print("\n[*] Generating visualization...")
        visualizer = MapVisualizer(elements)
        output_file = 'declutter_demo.png'
        visualizer.visualize_comparison(stats, save_path=output_file)
        
        print("\n[✓] Demo complete!")
        print(f"[✓] Check '{output_file}' for the before/after comparison")
        
    except ImportError as e:
        print(f"[ERROR] Import failed: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())