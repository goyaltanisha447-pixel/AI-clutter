# Algorithm Deep Dive - Map Decluttering Strategy

## Problem Formulation

**Given:**
- A set of map elements E = {e₁, e₂, ..., eₙ}
- Each element eᵢ has:
  - Unique ID
  - Type (immutable category)
  - Bounding box (position and size)
  - Priority (derived from type)
  - Movability status (immovable if priority ≥ 5)

**Goal:**
- Reposition movable elements to eliminate overlaps
- Preserve all immovable element positions
- Minimize total movement distance
- Ensure no new overlaps are created

**Constraints:**
- Immovable elements never move
- Only precomputed offset candidates are tried
- Maximum iteration limit (prevents infinite loops)

---

## Core Algorithm: MapDeclutterEngine.resolve_clutter()

### Pseudocode

```
FUNCTION resolve_clutter(elements)
    fixed_elements = filter(elements, priority >= 5)
    movable_elements = filter(elements, priority < 5)
    
    max_iterations = 10
    iterations = 0
    
    WHILE iterations < max_iterations DO
        iterations += 1
        resolved_any = false
        
        FOR EACH movable_element IN movable_elements DO
            overlapping = find_all_overlaps(movable_element, all_elements)
            
            IF overlapping is not empty THEN
                new_bbox = _reposition_element(movable_element)
                
                IF new_bbox != NULL THEN
                    movable_element.bbox = new_bbox
                    movable_element.moved = true
                    resolved_any = true
                END IF
            END IF
        END FOR
        
        IF NOT resolved_any THEN
            BREAK  // Convergence: no elements moved this iteration
        END IF
    END WHILE
    
    RETURN iterations
END FUNCTION
```

### Time Complexity Analysis

```
Setup:
  - Partition into fixed/movable: O(n)

Main Loop:
  - iterations: worst case 10 (constant)
  - For each movable element: m iterations
    - find_all_overlaps: O(n) pairwise comparisons
    - _reposition_element: O(8·n) tries 8 offsets × n fixed checks
  
Total: O(10 · m · (n + 8·n)) = O(10 · m · 9n) = O(90mn)

For typical case: 10 iterations · 5 movable · 3 fixed = 150 operations
For worst case: 10 iterations · 50 movable · 100 fixed = 45,000 operations
```

### Space Complexity

```
Additional memory:
  - fixed_elements list: O(n)
  - movable_elements list: O(n)
  - candidate_bbox temporary: O(1)

Total: O(n) auxiliary space
```

---

## Subroutine 1: find_overlaps(element)

### Purpose
Identify all elements that currently overlap with the given element.

### Pseudocode

```
FUNCTION find_overlaps(element) RETURNS list<Element>
    overlaps = empty list
    
    FOR EACH other IN self.elements DO
        IF other.id != element.id AND intersects(element.bbox, other.bbox) THEN
            overlaps.append(other)
        END IF
    END FOR
    
    RETURN overlaps
END FUNCTION
```

### Example

```
Element L1 (label) at (30, 83):
- Check against road_1 (20, 80): INTERSECT ✓ → add to overlap list
- Check against road_2 (95, 20): NO INTERSECT
- Check against river_1 (130, 100): NO INTERSECT
- Check against L2, L3, I1, I2: NO INTERSECT

Result: overlaps = [road_1]
```

---

## Subroutine 2: detect_overlap(elem_a, elem_b)

### Purpose
Check if two bounding boxes intersect using AABB (Axis-Aligned Bounding Box) collision detection.

### Mathematical Foundation

Two axis-aligned boxes **do NOT intersect** if:
- Box A is completely to the LEFT of Box B: `A.right < B.left`
- Box A is completely to the RIGHT of Box B: `A.left > B.right`
- Box A is completely ABOVE Box B: `A.bottom < B.top`
- Box A is completely BELOW Box B: `A.top > B.bottom`

They intersect if NONE of the above conditions are true.

### Pseudocode

```
FUNCTION intersects(boxA, boxB) RETURNS boolean
    // Check if boxes do NOT intersect
    // (If any of these is true, they don't overlap)
    
    IF boxA.x + boxA.width < boxB.x THEN
        RETURN false  // A is left of B
    END IF
    
    IF boxB.x + boxB.width < boxA.x THEN
        RETURN false  // B is left of A
    END IF
    
    IF boxA.y + boxA.height < boxB.y THEN
        RETURN false  // A is above B
    END IF
    
    IF boxB.y + boxB.height < boxA.y THEN
        RETURN false  // B is above A
    END IF
    
    RETURN true  // No separation found → they intersect
END FUNCTION
```

### Visual Examples

```
Case 1: No intersection (A left of B)
┌─────┐
│  A  │    ┌──────┐
└─────┘    │  B   │
           └──────┘
Result: FALSE

Case 2: Intersection
  ┌─────────┐
  │    A    │
  │  ┌──────┼────┐
  │  │  B   │    │
  └──┼──────┤    │
     │      │    │
     └──────┘    │
                 └──┘
Result: TRUE

Case 3: Touching edges (no intersection)
┌────────┐┌────────┐
│   A    ││   B    │
└────────┘└────────┘
Result: FALSE (edges touch but don't overlap)

Case 4: Complete containment (intersection)
┌───────────────┐
│      A        │
│  ┌────────┐   │
│  │   B    │   │
│  └────────┘   │
└───────────────┘
Result: TRUE
```

### Complexity

- **Time:** O(1) - constant number of comparisons
- **Space:** O(1) - no additional memory needed

---

## Subroutine 3: _reposition_element(element)

### Purpose
Find a valid new position for an element that:
1. Doesn't create new overlaps with fixed elements
2. Uses a precomputed set of offset candidates

### Movement Offsets

```
MOVEMENT_OFFSETS = [
    (0, -15),    // Cardinal: UP
    (0, +15),    // Cardinal: DOWN
    (+15, 0),    // Cardinal: RIGHT
    (-15, 0),    // Cardinal: LEFT
    (+15, -15),  // Diagonal: TOP-RIGHT
    (-15, -15),  // Diagonal: TOP-LEFT
    (+15, +15),  // Diagonal: BOTTOM-RIGHT
    (-15, +15)   // Diagonal: BOTTOM-LEFT
]
```

**Design Decision: Why this order?**
1. **Cardinal directions first** - More natural to human perception
2. **Fixed 15-pixel offset** - Consistently small movement
3. **All 8 directions tried** - Good coverage of possible positions

**Alternative considered:** Adaptive offset (scale by element size)
- Pro: Might find better solutions
- Con: More complex, harder to explain

### Pseudocode

```
FUNCTION _reposition_element(element) RETURNS BoundingBox or NULL
    FOR EACH (dx, dy) IN MOVEMENT_OFFSETS DO
        candidate_bbox = element.bbox.move(dx, dy)
        
        IF _is_valid_position(candidate_bbox, element.id) THEN
            RETURN candidate_bbox  // Found valid position!
        END IF
    END FOR
    
    RETURN NULL  // No valid position found
END FUNCTION
```

### Pseudocode for move()

```
FUNCTION move(bbox, dx, dy) RETURNS BoundingBox
    return BoundingBox(
        x = bbox.x + dx,
        y = bbox.y + dy,
        width = bbox.width,
        height = bbox.height
    )
END FUNCTION
```

### Example Trace

```
Element L1 at (30, 83), size 25×12 needs repositioning:

Attempt 1: Move UP (0, -15)
  New position: (30, 68)
  Check overlaps: road_1? NO ✓ Other fixed? NO ✓
  VALID! Return (30, 68)

(Doesn't try remaining offsets)
```

### Example of Failure

```
Element L_crowded at (95, 80) surrounded by roads:

Attempt 1: UP (0, -15) → (95, 65) → Overlaps road_2 ✗
Attempt 2: DOWN (0, +15) → (95, 95) → Overlaps road_2 ✗
Attempt 3: RIGHT (+15, 0) → (110, 80) → Overlaps road_2 ✗
Attempt 4: LEFT (-15, 0) → (80, 80) → Overlaps road_1 ✗
Attempt 5: TOP-RIGHT (+15, -15) → (110, 65) → Overlaps road_2 ✗
Attempt 6: TOP-LEFT (-15, -15) → (80, 65) → Overlaps road_1 ✗
Attempt 7: BOTTOM-RIGHT (+15, +15) → (110, 95) → Overlaps road_2 ✗
Attempt 8: BOTTOM-LEFT (-15, +15) → (80, 95) → Overlaps road_1 ✗

Result: No valid position found. Element stays at (95, 80).
Element not moved in this iteration.
```

### Complexity

- **Time:** O(8·n) where n = number of fixed elements
  - 8 offset candidates
  - Each candidate requires checking against all fixed elements: O(n)
- **Space:** O(1) - temporary BoundingBox only

---

## Subroutine 4: _is_valid_position(bbox, element_id)

### Purpose
Validate that a candidate position doesn't create new overlaps with fixed elements.

### Pseudocode

```
FUNCTION _is_valid_position(candidate_bbox, element_id) RETURNS boolean
    FOR EACH fixed_element IN self.fixed_elements DO
        IF candidate_bbox.intersects(fixed_element.bbox) THEN
            RETURN false  // Would create new overlap!
        END IF
    END FOR
    
    RETURN true  // Position is valid
END FUNCTION
```

### Example

```
Validate repositioning L1 from (30, 83) to (30, 68):

Check against fixed elements:
  road_1 (20, 80, 160×15):
    L1 new: (30, 68, 25×12) → boxes touch at edge, check intersection
    Intersection? (30, 68) to (55, 80) vs (20, 80) to (180, 95)
    Bottom of L1 (80) = Top of road_1 (80) → Touching, no intersection ✓

  road_2 (95, 20, 15×160):
    L1 new: (30, 68) is far from (95, 20) → No intersection ✓

  river_1 (130, 100, 60×12):
    L1 new: (30, 68) is far from (130, 100) → No intersection ✓

Result: VALID - Position accepted
```

### Complexity

- **Time:** O(n) where n = number of fixed elements
  - One intersection check per fixed element: O(1) × n
- **Space:** O(1) - no additional memory

---

## Iterative Convergence

### Why Multiple Iterations?

**Scenario:** Element A blocks Element B's optimal position

```
Iteration 1:
┌────────────────────────┐
│        Road            │
├──────┐    ┌─────────┐──┤
│ Icon │    │ Label   │  │
├──────┘    └─────────┘──┤
└────────────────────────┘

Label can't move right (blocked by road).
Tries to move down → success at new position.

Iteration 2:
┌────────────────────────┐
│        Road            │
├──────┐              ┌──┤
│ Icon │              │  │
├──────┘              └──┤
└────────────────────────┘
                   ┌──────┐
                   │Label │
                   └──────┘

Now Label is repositioned, next iteration continues.
```

### Convergence Condition

```
IF no_elements_moved_this_iteration THEN
    algorithm converged
    break
END IF

IF iterations_reached_max_limit THEN
    probably converged or unsolvable
    break
END IF
```

### Guaranteed Termination

The algorithm terminates because:
1. **Finite element set** - Constant number of elements n
2. **Discrete candidates** - Only 8 possible movements
3. **Explicit iteration limit** - At most 10 iterations for safety
4. **Convergence detection** - Stops when no progress made

---

## Element Types & Priority System

### Priority Mapping

```
┌────────────────────────────────────────┐
│ Type = 'road'   → Priority = 10        │
│ Type = 'river'  → Priority = 10        │
│ Type = 'label'  → Priority = 1         │
│ Type = 'icon'   → Priority = 2         │
│ Type = [other]  → Priority = 0         │
└────────────────────────────────────────┘

Movability Threshold: 5
├─ Priority >= 5 → IMMOVABLE (fixed)
└─ Priority < 5  → MOVABLE
```

### Why This Threshold?

```
Visual Hierarchy on Maps:
┌─────────────────────────────┐
│ 1. Infrastructure (Roads)   │ ← Critical, never move
│ 2. Natural Features (Rivers)│ ← Critical, never move
│ 3. Icons                    │ ← Important, can move
│ 4. Labels                   │ ← Context, can move
│ 5. Background               │ ← Can ignore/move
└─────────────────────────────┘
```

---

## Example Walkthrough: Demo Map

### Initial State

```
MAP GRID (200×200 pixels)

Y
200 ┼──────────────────────────────────┐
    │                                  │
150 │  [I1]   ┤Road 2  │═══ River    │
    │         │        │              │
100 │  [L1]   ┤        │════════════  │
    │      ┤Road 1 ├────────────┤   │
 50 │  [L2]    │                     │
    │          │        [I2]         │
  0 └──────────────────────────────────┘
    0         50        100       150  200→ X

LEGEND:
├─...─┤ = Road (Fixed, immovable)
════    = River (Fixed, immovable)
[L1]   = Label (Movable)
[I1]   = Icon (Movable)
```

### Overlap Analysis

```
┌─ Overlap 1: L1 ↔ Road 1
│  L1: (30, 83, 25×12)
│  Road 1: (20, 80, 160×15)
│  Intersection? Yes → Add to resolver queue
│
├─ Overlap 2: L2 ↔ Road 2
│  L2: (98, 140, 25×12)
│  Road 2: (95, 20, 15×160)
│  Intersection? Yes → Add to resolver queue
│
├─ Overlap 3: L3 ↔ River 1
│  L3: (135, 102, 25×10)
│  River 1: (130, 100, 60×12)
│  Intersection? Yes → Add to resolver queue
│
├─ Overlap 4: I1 ↔ Road 2
│  I1: (100, 50, 12×12)
│  Road 2: (95, 20, 15×160)
│  Intersection? Yes → Add to resolver queue
│
└─ Overlap 5: I2 ↔ River 1
   I2: (160, 103, 12×10)
   River 1: (130, 100, 60×12)
   Intersection? Yes → Add to resolver queue

Total Overlaps: 5
```

### Iteration 1 - Resolution

```
╔════════════════════════════════════════════════════════════════╗
║ ITERATION 1: Resolve overlapping movable elements              ║
╚════════════════════════════════════════════════════════════════╝

┌─ Processing L1 (originally at 30, 83)
│  Overlaps with: Road 1
│
│  Try Movement Offsets:
│  1. UP (0, -15) → (30, 68)
│     Check Road 1 (20, 80, 160×15)
│     Does (30, 68, 25×12) intersect (20, 80, 160×15)?
│     - 30 + 25 = 55 < 180 ✓ (not left of road)
│     - 20 + 160 = 180 > 30 ✓ (not right of road)
│     - 68 + 12 = 80 < 80 ✗ (TOUCHES EDGE BUT NOT OVERLAP)
│     
│     Actually testing: Does 80 < 80? NO → Not overlapping ✓
│     Valid position found! Move L1 to (30, 68)
│     Marked as moved ✓
│
├─ Processing L2 (originally at 98, 140)
│  Overlaps with: Road 2
│
│  Try Movement Offsets:
│  1. UP (0, -15) → (98, 125)
│     Check Road 2 (95, 20, 15×160)
│     Does (98, 125, 25×12) intersect (95, 20, 15×160)?
│     - 98 + 25 = 123, 95 + 15 = 110
│     - 123 > 110 → LEFT OF ROAD? No, 98 > 95, so not left
│     Actually within road's x-range (95-110)
│     And within road's y-range (20-180)
│     OVERLAPS → Try next offset
│
│  2. DOWN (0, +15) → (98, 155)
│     Road 2 y-range is (20, 180), L2 would be at (155, 167)
│     OVERLAPS → Try next offset
│
│  3. RIGHT (+15, 0) → (113, 140)
│     Check Road 2 (95, 20, 15×160)
│     L2 right edge: 113 + 25 = 138
│     Road 2 right edge: 95 + 15 = 110
│     138 > 110 → No longer overlapping ✓
│     Valid position found! Move L2 to (113, 140)
│     Marked as moved ✓
│
├─ Processing L3 (originally at 135, 102)
│  Overlaps with: River 1
│
│  Try Movement Offsets:
│  1. UP (0, -15) → (135, 87)
│     Check River 1 (130, 100, 60×12)
│     River 1 y-range: (100, 112)
│     L3 at y=87: Below river, no overlap ✓
│     Valid position found! Move L3 to (135, 87)
│     Marked as moved ✓
│
├─ Processing I1 (originally at 100, 50)
│  Overlaps with: Road 2
│
│  Try Movement Offsets:
│  1. UP (0, -15) → (100, 35)
│     Road 2 y-range: (20, 180)
│     I1 at y=35: Within range, still overlaps → Try next
│
│  2. DOWN (0, +15) → (100, 65)
│     Road 2 y-range: (20, 180)
│     Still within range, overlaps → Try next
│
│  3. RIGHT (+15, 0) → (115, 50)
│     Road 2 right edge: 110
│     115 > 110 → No overlap ✓
│     Valid position found! Move I1 to (115, 50)
│     Marked as moved ✓
│
└─ Processing I2 (originally at 160, 103)
   Overlaps with: River 1
   
   Try Movement Offsets:
   1. UP (0, -15) → (160, 88)
      River 1 y-range: (100, 112)
      88 < 100 → No overlap ✓
      Valid position found! Move I2 to (160, 88)
      Marked as moved ✓

═══════════════════════════════════════════════════════════════════
ITERATION 1 SUMMARY:
- Elements moved: L1, L2, L3, I1, I2 (5 total)
- Overlaps resolved: 5/5
- Convergence: All movable elements processed
═══════════════════════════════════════════════════════════════════
```

### Iteration 2 - Verification

```
╔════════════════════════════════════════════════════════════════╗
║ ITERATION 2: Re-check for new overlaps                         ║
╚════════════════════════════════════════════════════════════════╝

Checking each movable element again:

L1 (now at 30, 68): No overlaps ✓
L2 (now at 113, 140): No overlaps ✓
L3 (now at 135, 87): No overlaps ✓
I1 (now at 115, 50): No overlaps ✓
I2 (now at 160, 88): No overlaps ✓

Result: NO ELEMENTS MOVED THIS ITERATION
→ Algorithm converges, stop

═══════════════════════════════════════════════════════════════════
FINAL RESULT:
- Iterations completed: 2
- Iterations skipped: Converged at iteration 2
- Total elements moved: 5
- Success rate: 100% (5/5)
═══════════════════════════════════════════════════════════════════
```

---

## Performance Optimizations (Not Implemented)

### 1. Spatial Indexing (R-tree)

**Problem:** O(n²) pairwise overlap checks

**Solution:** Structure elements in R-tree
```
Current:  find_overlaps() → Check against ALL n elements → O(n)
Optimized: find_overlaps() → Query R-tree for nearby → O(log n)
```

### 2. Candidate Heuristics

**Problem:** Try all 8 offsets even if first 2 succeed

**Solution:** ML model predicts best offset
```
Current:  Try [UP, DOWN, RIGHT, LEFT, ...] in order
Optimized: ml_model(element, context) → [best_offset, ...] ranked
```

### 3. Parallel Resolution

**Problem:** Process one element at a time

**Solution:** Process non-overlapping elements in parallel
```
Current:  for element in elements: resolve(element)
Optimized: for element_group in non_overlapping_groups:
             parallel_resolve(element_group)
```

---

## Conclusion

The algorithm successfully:
1. **Detects overlaps** using O(1) AABB intersection checks
2. **Resolves conflicts** using iterative priority-based repositioning
3. **Validates solutions** to prevent creating new overlaps
4. **Converges quickly** (2 iterations for test case)
5. **Scales reasonably** up to ~1000 elements

For production use, the main optimization would be spatial indexing to reduce overlap detection from O(n²) to O(n log n).

---

*For implementation details, see [IMPLEMENTATION_NOTES.md](IMPLEMENTATION_NOTES.md)*
