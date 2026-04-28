use pyo3::prelude::*;
use std::collections::HashSet;

use crate::siatec::build_tecs_from_mtps;
use crate::tec::TranslationalEquivalence;

/// RecurSIA applied to COSIATEC: recursively compress patterns.
#[pyfunction]
pub fn recursive_cosiatec_compress(
    py: Python,
    dataset: Vec<(u32, u32)>,
    restrict_dpitch_zero: bool,
    min_pattern_size: usize,
) -> PyResult<Vec<TranslationalEquivalence>> {
    let mut remaining: HashSet<(u32, u32)> = dataset.iter().copied().collect();
    let mut tec_list = Vec::new();

    while !remaining.is_empty() {
        // 1. Find all TECs on remaining points
        let mut pts_list: Vec<(u32, u32)> = remaining.iter().copied().collect();
        pts_list.sort();
        let all_tecs = build_tecs_from_mtps(pts_list, restrict_dpitch_zero);

        if all_tecs.is_empty() {
            // No pattern found → output each remaining point as a trivial TEC
            for p in remaining {
                let pattern = vec![p];
                let translators = HashSet::new();
                let tec = TranslationalEquivalence::new(pattern, translators, None);
                tec_list.push(tec);
            }
            break;
        }

        // 2. Select best TEC (same criteria as COSIATEC)
        // Convert remaining to HashSet<(i64, i64)> for compactness/coverage methods
        let remaining_i64: HashSet<(i64, i64)> = remaining
            .iter()
            .map(|&(x, y)| (x as i64, y as i64))
            .collect();

        let mut best_idx = 0;
        let mut best_key = (
            all_tecs[0].compression_ratio(py)?,
            all_tecs[0].compactness(remaining_i64.clone()),
            all_tecs[0].coverage(py)?.len(),
        );
        for (idx, tec) in all_tecs.iter().enumerate().skip(1) {
            let key = (
                tec.compression_ratio(py)?,
                tec.compactness(remaining_i64.clone()),
                tec.coverage(py)?.len(),
            );
            if key > best_key {
                best_key = key;
                best_idx = idx;
            }
        }

        // 3. Clone the best TEC and recurse (if pattern is large enough)
        let mut best = all_tecs[best_idx].clone();
        if best.pattern.len() >= min_pattern_size {
            let sub_tecs = recursive_cosiatec_compress(
                py,
                best.pattern.clone(), // pattern is Vec<(u32, u32)>, fine
                restrict_dpitch_zero,
                min_pattern_size,
            )?;
            best.sub_tecs = sub_tecs;
        } else {
            best.sub_tecs = Vec::new();
        }

        tec_list.push(best);

        // 4. Remove covered points from remaining set
        let coverage = all_tecs[best_idx].coverage(py)?; // returns HashSet<(i64, i64)>
        // Convert coverage back to u32 for removal (safe because coordinates are within u32 range)
        let coverage_u32: HashSet<(u32, u32)> = coverage
            .iter()
            .map(|&(x, y)| (x as u32, y as u32))
            .collect();
        remaining.retain(|p| !coverage_u32.contains(p));
    }

    Ok(tec_list)
}