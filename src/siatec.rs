use pyo3::prelude::*;
use std::collections::HashSet;

use crate::sia::find_mtps;
use crate::tec::TranslationalEquivalence;

/// SIATEC algorithm: for each MTP find its TEC (all occurrences).
/// Returns a list of TECs (one per MTP).
#[pyfunction]
pub fn build_tecs_from_mtps(dataset: Vec<(u32, u32)>, restrict_dpitch_zero: bool) -> Vec<TranslationalEquivalence> {
    // Store dataset as i64 HashSet for easy containment checks
    let points_set: HashSet<(i64, i64)> = dataset.iter().map(|&(x, y)| (x as i64, y as i64)).collect();
    let mtps = find_mtps(dataset, restrict_dpitch_zero); // returns Vec<((i32,i32), Vec<(u32,u32)>)>
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

        let p0 = pattern[0]; // (u32, u32)
        // Collect all candidate translation vectors w = q - p0  (signed differences)
        let candidates: HashSet<(i32, i32)> = points_set
            .iter()
            .map(|&(qx, qy)| ((qx - p0.0 as i64) as i32, (qy - p0.1 as i64) as i32))
            .collect();

        let mut translators = HashSet::<(i32, i32)>::new();
        for w in candidates {
            if w == (0, 0) {
                continue;
            }
            if restrict_dpitch_zero && w.1 != 0 {
                continue;
            }
            // Check if pattern + w is fully contained in dataset
            let ok = pattern.iter().all(|&(px, py)| {
                let tx = px as i64 + w.0 as i64;
                let ty = py as i64 + w.1 as i64;
                points_set.contains(&(tx, ty))
            });
            if ok {
                translators.insert(w);
            }
        }

        if !translators.is_empty() {
            let tec = TranslationalEquivalence::new(pattern, translators, None);
            tecs.push(tec);
        }
    }

    tecs
}