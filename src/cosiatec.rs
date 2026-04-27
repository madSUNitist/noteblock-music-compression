use pyo3::prelude::*;
use std::collections::HashSet;

use crate::siatec::siatec;
use crate::tec::TEC;

/// COSIATEC greedy compression algorithm.
/// Returns a list of TECs covering the dataset.
#[pyfunction]
pub fn cosiatec(
    py: Python,
    dataset: Vec<(i64, i64)>,
    restrict_dpitch_zero: bool,
) -> PyResult<Vec<TEC>> {
    let mut remaining: HashSet<(i64, i64)> = dataset.iter().copied().collect();
    let mut tec_list = Vec::new();

    while !remaining.is_empty() {
        // Compute all TECs on the remaining points
        let mut pts_list: Vec<(i64, i64)> = remaining.iter().copied().collect();
        pts_list.sort();
        let all_tecs = siatec(pts_list, restrict_dpitch_zero);

        if all_tecs.is_empty() {
            // No more patterns → output each remaining point as a trivial TEC
            for p in remaining {
                let pattern = vec![p];
                let translators = HashSet::new();
                let tec = TEC::new(pattern, translators, None);
                tec_list.push(tec);
            }
            break;
        }

        // Select the best TEC according to (compression_ratio, compactness, coverage_len)
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

        let best = &all_tecs[best_idx];
        let coverage = best.coverage(py)?;
        tec_list.push(best.clone());
        // Remove all points covered by this TEC
        remaining.retain(|p| !coverage.contains(p));
    }

    Ok(tec_list)
}

/// Convert a list of TECs to a human‑readable encoding.
/// Each element: (pattern_points, list_of_translators)
#[pyfunction]
pub fn compress_to_encoding(
    py: Python,
    tecs: Vec<Py<TEC>>,
) -> PyResult<Vec<(Vec<(i64, i64)>, Vec<(i64, i64)>)>> {
    let mut encoding = Vec::new();
    for tec_py in tecs {
        let tec = tec_py.borrow(py);
        let pattern = tec.pattern.clone();
        let translators: Vec<(i64, i64)> = tec.translators.iter().copied().collect();
        encoding.push((pattern, translators));
    }
    Ok(encoding)
}