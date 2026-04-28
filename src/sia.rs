use pyo3::prelude::*;
use std::collections::HashMap;
use std::collections::HashSet;

/// Run the SIA (Sequential Interactive Algorithm) to find all maximal translatable patterns.
/// 
/// # Arguments
/// * `dataset` - A list of points, each as a tuple `(tick, pitch)` with non‑negative values.
/// * `restrict_dpitch_zero` - If true, only consider vectors with zero pitch difference.
/// 
/// # Returns
/// A vector of `(vector, start_points)` where `vector` is `(dtick, dpitch)`
/// and `start_points` is a sorted list of points that form the pattern.
#[pyfunction]
pub fn find_mtps(
    dataset: Vec<(u32, u32)>,
    restrict_dpitch_zero: bool,
) -> Vec<((i32, i32), Vec<(u32, u32)>)> {
    let points = dataset;                     // no sorting, keep as is
    let n = points.len();

    // Online grouping using HashMap to avoid storing all O(n²) pairs
    let mut groups: HashMap<(i32, i32), HashSet<(u32, u32)>> = HashMap::new();

    for i in 0..n {
        let (ti, pi) = points[i];
        for j in 0..n {
            if i == j {
                continue;
            }
            let (tj, pj) = points[j];
            // Compute vector (i32 range, differences may be negative)
            let dx = ti as i32 - tj as i32;
            let dy = pi as i32 - pj as i32;
            if restrict_dpitch_zero && dy != 0 {
                continue;
            }
            // Insert into group with pj as the starting point
            groups
                .entry((dx, dy))
                .or_insert_with(HashSet::new)
                .insert((tj, pj));
        }
    }

    // Collect results, filtering out zero vector and groups with fewer than 2 start points
    let mut result = Vec::new();
    for (vec, start_set) in groups {
        if vec == (0, 0) {
            continue;
        }
        if start_set.len() < 2 {
            continue;
        }
        // Convert to sorted Vec
        let mut start_points: Vec<_> = start_set.into_iter().collect();
        start_points.sort();                 // sort by (tick, pitch)
        result.push((vec, start_points));
    }
    result
}