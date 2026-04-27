use pyo3::prelude::*;
use std::collections::HashSet;

use crate::siatec::siatec;
use crate::tec::TEC;

/// RecurSIA applied to COSIATEC: recursively compress patterns.
#[pyfunction]
pub fn recur_sia_cosiatec(
    py: Python,
    dataset: Vec<(i64, i64)>,
    restrict_dpitch_zero: bool,
    min_pattern_size: usize,
) -> PyResult<Vec<TEC>> {
    let mut remaining: HashSet<(i64, i64)> = dataset.iter().copied().collect();
    let mut tec_list = Vec::new();

    while !remaining.is_empty() {
        // 1. Find all TECs on remaining points
        let mut pts_list: Vec<_> = remaining.iter().copied().collect();
        pts_list.sort();
        let all_tecs = siatec(pts_list, restrict_dpitch_zero);

        if all_tecs.is_empty() {
            // No pattern found → output each remaining point as a trivial TEC
            for p in remaining {
                let pattern = vec![p];
                let translators = HashSet::new();
                let tec = TEC::new(pattern, translators, None);
                tec_list.push(tec);
            }
            break;
        }

        // 2. Select best TEC (same criteria as COSIATEC)
        let mut best_idx = 0;
        let mut best_key = (
            all_tecs[0].compression_ratio(py)?,
            all_tecs[0].compactness(remaining.clone()),
            all_tecs[0].coverage(py)?.len(),
        );
        for (idx, tec) in all_tecs.iter().enumerate().skip(1) {
            let key = (
                tec.compression_ratio(py)?,
                tec.compactness(remaining.clone()),
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
            let sub_tecs = recur_sia_cosiatec(
                py,
                best.pattern.clone(),
                restrict_dpitch_zero,
                min_pattern_size,
            )?;
            best.sub_tecs = sub_tecs;
        } else {
            best.sub_tecs = Vec::new();
        }

        tec_list.push(best);

        // 4. Remove covered points from remaining set
        let coverage = all_tecs[best_idx].coverage(py)?;
        remaining.retain(|p| !coverage.contains(p));
    }

    Ok(tec_list)
}