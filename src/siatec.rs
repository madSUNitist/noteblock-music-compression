use pyo3::prelude::*;
use std::collections::HashSet;

use crate::sia::sia;
use crate::tec::TEC;

/// SIATEC algorithm: for each MTP find its TEC (all occurrences).
/// Returns a list of TECs (one per MTP).
#[pyfunction]
pub fn siatec(dataset: Vec<(i64, i64)>, restrict_dpitch_zero: bool) -> Vec<TEC> {
    let points_set: HashSet<(i64, i64)> = dataset.iter().copied().collect();
    let mtps = sia(dataset.clone(), restrict_dpitch_zero);
    let mut tecs = Vec::new();

    for (v, start_pts) in mtps {
        if v == (0, 0) {
            continue;
        }
        // pattern is the set of points that can be translated by v
        let pattern = start_pts; // already sorted and deduped by sia
        if pattern.is_empty() {
            continue;
        }

        let p0 = pattern[0];
        // Collect all candidate translation vectors w = q - p0
        let candidates: HashSet<(i64, i64)> = dataset
            .iter()
            .map(|q| (q.0 - p0.0, q.1 - p0.1))
            .collect();

        let mut translators = HashSet::new();
        for w in candidates {
            if w == (0, 0) {
                continue;
            }
            if restrict_dpitch_zero && w.1 != 0 {
                continue;
            }
            // Check if pattern + w is fully contained in dataset
            let ok = pattern.iter().all(|p| {
                let translated = (p.0 + w.0, p.1 + w.1);
                points_set.contains(&translated)
            });
            if ok {
                translators.insert(w);
            }
        }

        if !translators.is_empty() {
            let tec = TEC::new(pattern, translators, None);
            tecs.push(tec);
        }
    }

    tecs
}

/// Compare two TECs according to the rules in ISBETTERTEC.
/// Returns true if tec1 is better than tec2.
#[pyfunction]
pub fn is_better_tec(
    py: Python,
    tec1: &TEC,
    tec2: &TEC,
    dataset_points: HashSet<(i64, i64)>,
) -> bool {
    // compression ratio
    let cr1 = tec1.compression_ratio(py).unwrap_or(0.0);
    let cr2 = tec2.compression_ratio(py).unwrap_or(0.0);
    if cr1 != cr2 {
        return cr1 > cr2;
    }
    // compactness
    let comp1 = tec1.compactness(dataset_points.clone());
    let comp2 = tec2.compactness(dataset_points);
    if comp1 != comp2 {
        return comp1 > comp2;
    }
    // coverage size
    let cov1 = tec1.coverage(py).map(|c| c.len()).unwrap_or(0);
    let cov2 = tec2.coverage(py).map(|c| c.len()).unwrap_or(0);
    if cov1 != cov2 {
        return cov1 > cov2;
    }
    // pattern size
    let len1 = tec1.pattern.len();
    let len2 = tec2.pattern.len();
    if len1 != len2 {
        return len1 > len2;
    }
    // temporal width (duration of pattern)
    let width1 = tec1.pattern.iter().map(|p| p.0).max().unwrap_or(0) -
                 tec1.pattern.iter().map(|p| p.0).min().unwrap_or(0);
    let width2 = tec2.pattern.iter().map(|p| p.0).max().unwrap_or(0) -
                 tec2.pattern.iter().map(|p| p.0).min().unwrap_or(0);
    if width1 != width2 {
        return width1 < width2;
    }
    // bounding box area (tick_range * pitch_range)
    let x1 = tec1.pattern.iter().map(|p| p.0).max().unwrap_or(0) -
             tec1.pattern.iter().map(|p| p.0).min().unwrap_or(0);
    let y1 = tec1.pattern.iter().map(|p| p.1).max().unwrap_or(0) -
             tec1.pattern.iter().map(|p| p.1).min().unwrap_or(0);
    let area1 = x1 * y1;
    let x2 = tec2.pattern.iter().map(|p| p.0).max().unwrap_or(0) -
             tec2.pattern.iter().map(|p| p.0).min().unwrap_or(0);
    let y2 = tec2.pattern.iter().map(|p| p.1).max().unwrap_or(0) -
             tec2.pattern.iter().map(|p| p.1).min().unwrap_or(0);
    let area2 = x2 * y2;
    area1 < area2
}