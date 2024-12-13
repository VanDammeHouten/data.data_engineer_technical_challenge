"""
Metrics for evaluating model performance.
"""

from typing import List, Tuple, Dict, Set
from ..models.bounding_box import BoundingBox

def calculate_precision(true_positives: int, no_predicted_boxes: int) -> float:
    """
    Calculate precision: ratio of correctly predicted boxes to total predictions.
    
    Args:
        true_positives: Number of correct predictions
        no_predicted_boxes: Number of predicted boxes
        
    Returns:
        float: Precision score between 0 and 1
    """
    return true_positives / no_predicted_boxes if no_predicted_boxes else 0

def calculate_recall(true_positives: int, no_ground_truth_boxes: int) -> float:
    """
    Calculate recall: ratio of correctly predicted boxes to total actual boxes.
    
    Args:
        true_positives: Number of correct predictions
        no_ground_truth_boxes: Number of ground truth boxes
        
    Returns:
        float: Recall score between 0 and 1
    """
    return true_positives / no_ground_truth_boxes if no_ground_truth_boxes else 0

def calculate_f1(precision: float, recall: float) -> float:
    """
    Calculate F1 score: harmonic mean of precision and recall.
    
    Args:
        precision: Precision score
        recall: Recall score
        
    Returns:
        float: F1 score between 0 and 1
    """
    return 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0


def find_true_positives(predicted_boxes: List[BoundingBox],
                       ground_truth_boxes: List[BoundingBox],
                       iou_threshold: float = 0.5) -> Tuple[int, Set[int]]:
    """
    Find the number of true positive predictions and their matching ground truth boxes.
    
    Args:
        predicted_boxes: List of predicted BoundingBox objects
        ground_truth_boxes: List of ground truth BoundingBox objects
        iou_threshold: Minimum IoU to consider a match
        
    Returns:
        Tuple containing:
            - Number of true positives
            - Set of indices of matched ground truth boxes
    """
    true_positives = 0
    matched_gt_boxes = set()
    
    for pred_box in predicted_boxes:
        best_iou = 0
        best_gt_idx = None
        
        for idx, gt_box in enumerate(ground_truth_boxes):
            if idx in matched_gt_boxes:
                continue
                
            iou = pred_box.calculate_iou(gt_box)
            if iou > best_iou:
                best_iou = iou
                best_gt_idx = idx
        
        if best_iou >= iou_threshold:
            true_positives += 1
            matched_gt_boxes.add(best_gt_idx)
    
    return true_positives, matched_gt_boxes

def calculate_metrics_for_predictions(predicted_boxes: List[BoundingBox],
                                    ground_truth_boxes: List[BoundingBox],
                                    iou_threshold: float = 0.5) -> Dict[str, float]:
    """
    Calculate all metrics for a set of predicted boxes against ground truth boxes.
    
    Args:
        predicted_boxes: List of predicted BoundingBox objects
        ground_truth_boxes: List of ground truth BoundingBox objects
        iou_threshold: Minimum IoU to consider a match
        
    Returns:
        Dictionary containing precision, recall, F1 score, and raw counts
    """
    true_positives, matched_gt_boxes = find_true_positives(
        predicted_boxes, ground_truth_boxes, iou_threshold
    )
    
    precision = calculate_precision(true_positives, len(predicted_boxes))
    recall = calculate_recall(true_positives, len(ground_truth_boxes))
    f1 = calculate_f1(precision, recall)
    
    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'true_positives': true_positives,
        'false_positives': len(predicted_boxes) - true_positives,
        'false_negatives': len(ground_truth_boxes) - true_positives,
        'labelled_boxes': len(ground_truth_boxes),
        'predicted_boxes': len(predicted_boxes)
    }

def find_box_matches(predicted_boxes: List[BoundingBox],
                    ground_truth_boxes: List[BoundingBox],
                    iou_threshold: float = 0.5) -> Dict[int, int]:
    """
    Find matching pairs of predicted and ground truth boxes based on IoU.
    
    Args:
        predicted_boxes: List of predicted BoundingBox objects
        ground_truth_boxes: List of ground truth BoundingBox objects
        iou_threshold: Minimum IoU to consider a match
        
    Returns:
        Dictionary mapping predicted box indices to ground truth box indices
        where key = predicted_box_index, value = ground_truth_box_index
    """
    matches = {}
    used_gt_boxes = set()
    
    for pred_idx, pred_box in enumerate(predicted_boxes):
        best_iou = iou_threshold
        best_gt_idx = None
        
        for gt_idx, gt_box in enumerate(ground_truth_boxes):
            if gt_idx in used_gt_boxes:
                continue
                
            iou = pred_box.calculate_iou(gt_box)
            if iou > best_iou:
                best_iou = iou
                best_gt_idx = gt_idx
        
        if best_gt_idx is not None:
            matches[pred_idx] = best_gt_idx
            used_gt_boxes.add(best_gt_idx)
    
    return matches