use pyo3::prelude::*;
use std::collections::HashSet;

use crate::siatec::build_tecs_from_mtps;
use crate::tec::TranslationalEquivalence;

/// COSIATEC greedy compression algorithm.
/// Returns a list of TECs covering the dataset.
#[pyfunction]
pub fn cosiatec_compress(
    py: Python,
    dataset: Vec<(u32, u32)>,
    restrict_dpitch_zero: bool,
) -> PyResult<Vec<TranslationalEquivalence>> {
    let mut remaining: HashSet<(u32, u32)> = dataset.iter().copied().collect();
    let mut tec_list = Vec::new();

    while !remaining.is_empty() {
        // Compute all TECs on the remaining points
        let mut pts_list: Vec<(u32, u32)> = remaining.iter().copied().collect();
        pts_list.sort();
        let all_tecs = build_tecs_from_mtps(pts_list, restrict_dpitch_zero);

        if all_tecs.is_empty() {
            // No more patterns → output each remaining point as a trivial TEC
            for p in remaining {
                let pattern = vec![p];
                let translators = HashSet::new();
                let tec = TranslationalEquivalence::new(pattern, translators, None);
                tec_list.push(tec);
            }
            break;
        }

        // Convert remaining to i64 for compactness and coverage methods
        let remaining_i64: HashSet<(i64, i64)> = remaining
            .iter()
            .map(|&(x, y)| (x as i64, y as i64))
            .collect();

        // Select the best TEC according to (compression_ratio, compactness, coverage_len)
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

        let best = &all_tecs[best_idx];
        let coverage = best.coverage(py)?; // HashSet<(i64, i64)>
        tec_list.push(best.clone());

        // Remove all points covered by this TEC (convert coverage back to u32 for comparison)
        let coverage_u32: HashSet<(u32, u32)> = coverage
            .iter()
            .map(|&(x, y)| (x as u32, y as u32))
            .collect();
        remaining.retain(|p| !coverage_u32.contains(p));
    }

    Ok(tec_list)
}