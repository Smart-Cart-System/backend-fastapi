from typing import List, Dict, Tuple, Set, Optional
import heapq
from sqlalchemy.orm import Session
from crud import aisle_layout, promotion, aisle as aisle_crud
from schemas.aisle_layout import NavigationStep, NavigationResponse
from models.promotion import PromotionData
import datetime

def find_optimal_path(
    db: Session, 
    start_aisle_id: int, 
    target_aisle_id: int
) -> NavigationResponse:
    """Find the optimal path between aisles, prioritizing promotions"""
    
    # Get all aisle positions and connections
    aisle_positions = {pos.aisle_id: pos for pos in aisle_layout.get_all_aisle_positions(db)}
    
    # Get all aisles
    all_aisles = {aisle.id: aisle for aisle in aisle_crud.get_aisles(db)}
    
    # Count active promotions for each aisle
    today = datetime.date.today()
    promotions_by_aisle = {}
    for aisle_id in all_aisles:
        promotions_by_aisle[aisle_id] = aisle_layout.get_aisle_promotions_count(db, aisle_id)
    
    # Get the connections between aisles
    connections = {}
    for aisle in all_aisles.values():
        connections[aisle.id] = [connected.id for connected in aisle.connected_to]
    
    # Implementation of A* algorithm with promotion weighting
    def heuristic(aisle_id: int) -> float:
        """Heuristic function: Manhattan distance to target"""
        if aisle_id not in aisle_positions or target_aisle_id not in aisle_positions:
            return float('inf')
            
        start_pos = aisle_positions[aisle_id]
        target_pos = aisle_positions[target_aisle_id]
        return abs(start_pos.x - target_pos.x) + abs(start_pos.y - target_pos.y)
    
    # Priority queue for A*
    open_set = [(0, start_aisle_id)]
    
    # For node-to-node path reconstruction
    came_from = {}
    
    # Cost from start to each node
    g_score = {aisle_id: float('inf') for aisle_id in all_aisles}
    g_score[start_aisle_id] = 0
    
    # Estimated total cost from start to goal through each node
    f_score = {aisle_id: float('inf') for aisle_id in all_aisles}
    f_score[start_aisle_id] = heuristic(start_aisle_id)
    
    # Set to track visited nodes
    visited = set()
    
    while open_set:
        _, current = heapq.heappop(open_set)
        
        if current == target_aisle_id:
            # Reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            
            path.append(start_aisle_id)
            path.reverse()
            
            # Build response with detailed information
            steps = []
            total_promotions = 0
            
            for aisle_id in path:
                aisle = all_aisles[aisle_id]
                position = aisle_positions.get(aisle_id)
                promo_count = promotions_by_aisle.get(aisle_id, 0)
                total_promotions += promo_count
                
                step = NavigationStep(
                    aisle_id=aisle_id,
                    name=aisle.name,
                    x=position.x if position else 0,
                    y=position.y if position else 0,
                    promotions_count=promo_count
                )
                steps.append(step)
            
            return NavigationResponse(
                path=steps,
                total_distance=len(steps) - 1,
                total_promotions=total_promotions,
                target_promotion_id=0,  # Will be set by caller
                target_aisle_id=target_aisle_id
            )
        
        visited.add(current)
        
        # Check all neighbors
        for neighbor in connections.get(current, []):
            if neighbor in visited:
                continue
                
            # Calculate distance (always 1 between adjacent aisles)
            distance = 1
            
            # Calculate the promotion "discount" - more promotions mean "shorter" effective distance
            promo_count = promotions_by_aisle.get(neighbor, 0)
            promo_factor = max(0.5, 1.0 - (promo_count * 0.1))  # Up to 50% discount based on promotions
            
            effective_distance = distance * promo_factor
            
            # Calculate tentative g_score
            tentative_g_score = g_score[current] + effective_distance
            
            if tentative_g_score < g_score[neighbor]:
                # Found a better path
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor)
                
                # Add to open set if not already there
                if neighbor not in [item[1] for item in open_set]:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
    
    # No path found
    return NavigationResponse(
        path=[],
        total_distance=0,
        total_promotions=0,
        target_promotion_id=0,
        target_aisle_id=target_aisle_id
    )

def find_path_to_promotion(
    db: Session, 
    session_id: int, 
    promotion_id: int
) -> Optional[NavigationResponse]:
    """Find path from session's current aisle to promotion's aisle"""
    # Get the promotion to find its aisle
    promotion_record = db.query(PromotionData).filter(PromotionData.index == promotion_id).first()
    if not promotion_record or not promotion_record.aisle_id:
        return None
        
    # Get target aisle
    target_aisle_id = promotion_record.aisle_id
    
    # Get session's current location
    current_aisle_id = aisle_layout.get_last_session_location(db, session_id)
    if not current_aisle_id:
        return None
    
    # If already at target aisle, return simple path
    if current_aisle_id == target_aisle_id:
        aisle_obj = aisle_crud.get_aisle(db, current_aisle_id)
        position = aisle_layout.get_aisle_position(db, current_aisle_id)
        promo_count = aisle_layout.get_aisle_promotions_count(db, current_aisle_id)
        
        return NavigationResponse(
            path=[NavigationStep(
                aisle_id=current_aisle_id,
                name=aisle_obj.name,
                x=position.x if position else 0,
                y=position.y if position else 0,
                promotions_count=promo_count
            )],
            total_distance=0,
            total_promotions=promo_count,
            target_promotion_id=promotion_id,
            target_aisle_id=target_aisle_id
        )
    
    # Find optimal path
    response = find_optimal_path(db, current_aisle_id, target_aisle_id)
    response.target_promotion_id = promotion_id
    
    return response