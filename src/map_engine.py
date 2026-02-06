"""
Map Declutter Engine - Core Algorithm
Implements priority-based overlap resolution for map elements
"""

class BoundingBox:
    """Represents a rectangular bounding box for map elements"""
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def intersects(self, other):
        """Check if this box overlaps with another box"""
        return not (
            self.x + self.width < other.x or
            other.x + other.width < self.x or
            self.y + self.height < other.y or
            other.y + other.height < self.y
        )
    
    def move(self, dx, dy):
        """Return a new BoundingBox moved by (dx, dy)"""
        return BoundingBox(self.x + dx, self.y + dy, self.width, self.height)
    
    def __repr__(self):
        return f"Box({self.x}, {self.y}, {self.width}x{self.height})"


class MapElement:
    """Represents a single element on the map"""
    
    # Priority levels (higher = more important, never moves)
    PRIORITY = {
        'road': 10,
        'river': 10,
        'label': 1,
        'icon': 2
    }
    
    def __init__(self, id, element_type, bbox):
        self.id = id
        self.type = element_type
        self.bbox = bbox
        self.priority = self.PRIORITY.get(element_type, 0)
        self.movable = self.priority < 5  # Low priority items are movable
        self.original_bbox = BoundingBox(bbox.x, bbox.y, bbox.width, bbox.height)
        self.moved = False
    
    def __repr__(self):
        return f"Element(id={self.id}, type={self.type}, movable={self.movable})"


class MapDeclutterEngine:
    """Main engine for detecting and resolving map clutter"""
    
    # Movement candidates (try these offsets in order)
    MOVEMENT_OFFSETS = [
        (0, -15),   # up
        (0, 15),    # down
        (15, 0),    # right
        (-15, 0),   # left
        (15, -15),  # diagonal top-right
        (-15, -15), # diagonal top-left
        (15, 15),   # diagonal bottom-right
        (-15, 15)   # diagonal bottom-left
    ]
    
    def __init__(self, elements):
        self.elements = elements
        self.fixed_elements = [e for e in elements if not e.movable]
        self.movable_elements = [e for e in elements if e.movable]
    
    def detect_overlap(self, elem_a, elem_b):
        """
        Detect if two elements overlap
        
        Args:
            elem_a: First MapElement
            elem_b: Second MapElement
            
        Returns:
            bool: True if bounding boxes intersect, False otherwise
        """
        return elem_a.bbox.intersects(elem_b.bbox)
    
    def find_overlaps(self, element):
        """
        Find all elements that overlap with the given element
        
        Args:
            element: Target MapElement
            
        Returns:
            list: List of MapElement objects that overlap with the target
        """
        overlaps = []
        for other in self.elements:
            if other.id != element.id and self.detect_overlap(element, other):
                overlaps.append(other)
        return overlaps
    
    def resolve_clutter(self):
        """
        Main algorithm: Iteratively resolve overlaps
        
        Strategy:
        1. Find movable elements that overlap with fixed (high-priority) elements
        2. Try to reposition them using minimal movements
        3. Ensure new position doesn't create new overlaps
        """
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            resolved_any = False
            
            # Check each movable element
            for movable in self.movable_elements:
                # Find overlaps with fixed elements (roads, rivers)
                overlaps = [e for e in self.find_overlaps(movable) if not e.movable]
                
                if overlaps:
                    # Try to reposition this element
                    new_bbox = self._reposition_element(movable)
                    if new_bbox:
                        movable.bbox = new_bbox
                        movable.moved = True
                        resolved_any = True
            
            # If no changes made, we're done
            if not resolved_any:
                break
        
        return iteration
    
    def _reposition_element(self, element):
        """
        Try to find a new position for an element that doesn't overlap
        
        Returns: New BoundingBox if successful, None otherwise
        """
        for dx, dy in self.MOVEMENT_OFFSETS:
            candidate_bbox = element.bbox.move(dx, dy)
            
            # Check if this position creates any new overlaps
            if self._is_valid_position(candidate_bbox, element.id):
                return candidate_bbox
        
        return None  # Couldn't find a valid position
    
    def _is_valid_position(self, bbox, element_id):
        """
        Check if a bounding box position is valid (no overlaps with fixed elements)
        
        This validation ensures that when repositioning a movable element,
        it doesn't create new overlaps with high-priority (fixed) elements.
        
        Args:
            bbox: BoundingBox to validate
            element_id: ID of the element being validated (for reference)
            
        Returns:
            bool: True if position is valid, False if it creates overlaps
        """
        for fixed in self.fixed_elements:
            if bbox.intersects(fixed.bbox):
                return False
        return True
    
    def get_statistics(self):
        """Return statistics about the decluttering process"""
        moved_count = sum(1 for e in self.movable_elements if e.moved)
        total_movable = len(self.movable_elements)
        
        return {
            'total_elements': len(self.elements),
            'fixed_elements': len(self.fixed_elements),
            'movable_elements': total_movable,
            'elements_moved': moved_count,
            'move_percentage': (moved_count / total_movable * 100) if total_movable > 0 else 0
        }