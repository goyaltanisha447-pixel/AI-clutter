# Quick Start Guide - Map Declutter AI

## 30-Second Setup

```bash
# 1. Install dependencies (one-time)
pip install -r requirements.txt

# 2. Run the demo
python src/demo.py

# 3. View the result
# → Opens visualization showing before/after
# → Saves 'declutter_demo.png' showing the comparison
```

## What You'll See

The demo creates a test map with:
- **3 fixed elements** (2 roads + 1 river) - shown as solid blocks in dark colors
- **5 movable elements** (3 labels + 2 icons) - shown as outlined boxes

**Before:** All elements overlapping on top of each other ⚠️  
**After:** Labels and icons have been repositioned to avoid the roads and river ✅

## Understanding the Output

```
🗺️  MAP DECLUTTER AI - HACKATHON DEMO
============================================

📍 Creating demo map with intentional overlaps...
✓ Created 8 map elements

🔍 ALGORITHM EXECUTION STEPS
============================================

1️⃣ ELEMENT CLASSIFICATION:
   • Fixed elements (roads, rivers): 3
   • Movable elements (labels, icons): 5

2️⃣ OVERLAP DETECTION:
   • L1 overlaps with: road_1
   • ... (other detected overlaps)

3️⃣ RUNNING RESOLUTION ALGORITHM...
   • Completed in 2 iterations

4️⃣ REPOSITIONING RESULTS:
   • L1: moved (0, +15) pixels
   • ... (other movements)

📊 FINAL STATISTICS
============================================
Total elements:       8
Fixed elements:       3
Movable elements:     5
Elements moved:       5
Success rate:         100.0%

🎨 Generating visualization...
✓ Visualization saved to declutter_demo.png
```

## Key Terms

| Term | Meaning |
|------|---------|
| **Overlap** | Two elements occupying the same space |
| **Fixed Elements** | Roads and rivers that never move (high priority) |
| **Movable Elements** | Labels and icons that can be repositioned |
| **Iteration** | One complete pass through all elements |
| **Success Rate** | Percentage of elements that could be repositioned |

## File Structure

```
src/
├── map_engine.py       ← Core algorithm
├── visualizer.py       ← Visualization
└── demo.py             ← Main demo script (run this!)

declutter_demo.png      ← Output (generated after running)
```

## Customizing the Demo

Want to modify the test map? Edit `src/demo.py`:

```python
def create_demo_map():
    """Create a demo map with intentional overlaps"""
    elements = []
    
    # Add your own elements here!
    elements.append(MapElement(
        id="road_1",
        element_type="road",
        bbox=BoundingBox(x, y, width, height)  # ← Your coordinates
    ))
    
    return elements
```

## Creating Your Own Maps Programmatically

```python
from src.map_engine import BoundingBox, MapElement, MapDeclutterEngine
from src.visualizer import MapVisualizer

# 1. Create elements
elements = [
    MapElement("my_road", "road", BoundingBox(10, 10, 100, 5)),
    MapElement("my_label", "label", BoundingBox(15, 12, 30, 8)),
    # ... more elements
]

# 2. Run algorithm
engine = MapDeclutterEngine(elements)
engine.resolve_clutter()

# 3. Visualize
stats = engine.get_statistics()
visualizer = MapVisualizer(elements)
visualizer.visualize_comparison(stats, save_path='my_map.png')
```

## Troubleshooting

### Error: `ModuleNotFoundError: No module named 'matplotlib'`
```bash
pip install -r requirements.txt
```

### Error: `No valid position found`
This is normal! Some elements might not be repositionable if the map is too crowded. The algorithm handles this gracefully.

### Error: `'charmap' codec can't encode character`
This is just a Unicode display issue with the Windows terminal. The demo still works fine - ignore it.

## System Requirements

- **Python:** 3.8 or newer
- **Memory:** ~50 MB
- **Disk:** ~30 MB (with dependencies)
- **Time:** ~1 second to run demo

## Next Steps

1. Read [README.md](README.md) for detailed algorithm explanation
2. Check [IMPLEMENTATION_NOTES.md](IMPLEMENTATION_NOTES.md) for technical details
3. Explore the source code in `src/` directory
4. Try modifying the demo to understand how the algorithm works

## Common Questions

**Q: Can I use this for my own maps?**  
A: Yes! The algorithm works with any rectangular elements. Just create `MapElement` objects with your data.

**Q: Why are some elements not moving?**  
A: Roads and rivers (fixed elements) never move by design. They have priority 10 and are immovable.

**Q: How does it decide where to move labels?**  
A: It tries movements in order: up, down, right, left, then diagonals. The first position that doesn't create new overlaps is chosen.

**Q: What if an element can't be moved?**  
A: It stays at its original position. The algorithm continues with other elements - no crash, no silent failure.

## Performance Notes

For production use:
- Current algorithm: O(k·m·n) where k=iterations, m=movable, n=fixed
- Demo map: 8 elements, completes in 2 iterations
- Scales to ~1000 elements before needing optimization
- For larger maps, consider spatial indexing (R-tree)

## License

MIT - Free to use and modify for any purpose.

---

**Built for the Map Declutter AI Hackathon Challenge** 🗺️
