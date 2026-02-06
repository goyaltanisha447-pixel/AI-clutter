"""
Map Declutter Visualizer
Creates before/after visualization of the decluttering algorithm
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch


class MapVisualizer:
    """Visualizes map elements and decluttering results"""
    
    # Color scheme for different element types
    COLORS = {
        'road': '#2C3E50',      # Dark blue-gray
        'river': '#3498DB',      # Blue
        'label': '#E74C3C',      # Red
        'icon': '#F39C12'        # Orange
    }
    
    def __init__(self, elements):
        self.elements = elements
    
    def draw_element(self, ax, element, show_original=False):
        """Draw a single element on the axes"""
        bbox = element.bbox
        color = self.COLORS.get(element.type, '#95A5A6')
        
        if element.type in ['road', 'river']:
            # Draw fixed elements as solid rectangles
            rect = FancyBboxPatch(
                (bbox.x, bbox.y), bbox.width, bbox.height,
                boxstyle="round,pad=0.05",
                linewidth=2,
                edgecolor=color,
                facecolor=color,
                alpha=0.7
            )
            ax.add_patch(rect)
            
            # Add label
            ax.text(
                bbox.x + bbox.width / 2,
                bbox.y + bbox.height / 2,
                element.type.upper(),
                ha='center', va='center',
                fontsize=8,
                color='white',
                weight='bold'
            )
        else:
            # Draw movable elements as outlined boxes with labels
            rect = FancyBboxPatch(
                (bbox.x, bbox.y), bbox.width, bbox.height,
                boxstyle="round,pad=0.05",
                linewidth=1.5,
                edgecolor=color,
                facecolor='white',
                alpha=0.8
            )
            ax.add_patch(rect)
            
            # Add label
            ax.text(
                bbox.x + bbox.width / 2,
                bbox.y + bbox.height / 2,
                f"{element.type}\n{element.id}",
                ha='center', va='center',
                fontsize=7,
                color=color,
                weight='bold'
            )
        
        # Show original position if element was moved
        if show_original and element.moved:
            orig_bbox = element.original_bbox
            orig_rect = patches.Rectangle(
                (orig_bbox.x, orig_bbox.y), orig_bbox.width, orig_bbox.height,
                linewidth=1,
                edgecolor='gray',
                facecolor='none',
                linestyle='--',
                alpha=0.5
            )
            ax.add_patch(orig_rect)
            
            # Draw arrow showing movement
            ax.annotate(
                '',
                xy=(bbox.x + bbox.width/2, bbox.y + bbox.height/2),
                xytext=(orig_bbox.x + orig_bbox.width/2, orig_bbox.y + orig_bbox.height/2),
                arrowprops=dict(arrowstyle='->', color='gray', lw=1, alpha=0.6)
            )
    
    def visualize_comparison(self, stats, save_path=None):
        """Create before/after comparison visualization"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # === BEFORE (Left Panel) ===
        ax1.set_title('BEFORE: Cluttered Map', fontsize=14, weight='bold', pad=20)
        ax1.set_xlim(-10, 210)
        ax1.set_ylim(-10, 210)
        ax1.set_aspect('equal')
        ax1.grid(True, alpha=0.2)
        ax1.set_xlabel('X Coordinate', fontsize=10)
        ax1.set_ylabel('Y Coordinate', fontsize=10)
        
        # Draw elements in original positions
        for element in self.elements:
            # Temporarily restore original position for display
            if element.moved:
                original_bbox = element.bbox
                element.bbox = element.original_bbox
                self.draw_element(ax1, element)
                element.bbox = original_bbox
            else:
                self.draw_element(ax1, element)
        
        # Add overlap indicators
        overlap_count = self._count_overlaps()
        ax1.text(
            100, -5,
            f"⚠️ {overlap_count} overlaps detected",
            ha='center', fontsize=10, color='red', weight='bold'
        )
        
        # === AFTER (Right Panel) ===
        ax2.set_title('AFTER: Decluttered Map', fontsize=14, weight='bold', pad=20)
        ax2.set_xlim(-10, 210)
        ax2.set_ylim(-10, 210)
        ax2.set_aspect('equal')
        ax2.grid(True, alpha=0.2)
        ax2.set_xlabel('X Coordinate', fontsize=10)
        ax2.set_ylabel('Y Coordinate', fontsize=10)
        
        # Draw elements in final positions
        for element in self.elements:
            self.draw_element(ax2, element, show_original=True)
        
        # Add statistics
        moved_text = (
            f"✓ {stats['elements_moved']}/{stats['movable_elements']} "
            f"labels repositioned ({stats['move_percentage']:.1f}%)"
        )
        ax2.text(
            100, -5,
            moved_text,
            ha='center', fontsize=10, color='green', weight='bold'
        )
        
        # Add legend
        legend_elements = [
            patches.Patch(facecolor=self.COLORS['road'], label='Road (Fixed)'),
            patches.Patch(facecolor=self.COLORS['river'], label='River (Fixed)'),
            patches.Patch(facecolor='white', edgecolor=self.COLORS['label'], label='Label (Movable)'),
            patches.Patch(facecolor='white', edgecolor=self.COLORS['icon'], label='Icon (Movable)'),
            patches.Patch(facecolor='none', edgecolor='gray', linestyle='--', label='Original Position')
        ]
        fig.legend(
            handles=legend_elements,
            loc='lower center',
            ncol=5,
            frameon=True,
            fontsize=9
        )
        
        plt.suptitle(
            'AI-Powered Map Decluttering Algorithm',
            fontsize=16,
            weight='bold',
            y=0.98
        )
        
        plt.tight_layout(rect=[0, 0.05, 1, 0.96])
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Visualization saved to {save_path}")
        
        plt.show()
    
    def _count_overlaps(self):
        """Count total number of overlaps in current state"""
        count = 0
        for i, elem_a in enumerate(self.elements):
            for elem_b in self.elements[i+1:]:
                if elem_a.bbox.intersects(elem_b.bbox):
                    count += 1
        return count