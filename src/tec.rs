use pyo3::prelude::*;

use std::fmt;
use std::collections::HashSet;

/// Translational Equivalence Class: a pattern + set of non-zero translators.
#[pyclass(from_py_object)]
#[derive(Clone)]
pub struct TranslationalEquivalence {
    /// Sorted pattern points (u32 range)
    #[pyo3(get)]
    pub pattern: Vec<(u32, u32)>,
    /// Non-zero translators (i32 differences)
    #[pyo3(get)]
    pub translators: HashSet<(i32, i32)>,
    /// Sub-TECs (optional)
    #[pyo3(get)]
    pub sub_tecs: Vec<TranslationalEquivalence>,
}

#[pymethods]
impl TranslationalEquivalence {
    #[new]
    pub fn new(
        pattern: Vec<(u32, u32)>,
        translators: HashSet<(i32, i32)>,
        sub_tecs: Option<Vec<TranslationalEquivalence>>,
    ) -> Self {
        let mut pattern_sorted = pattern;
        pattern_sorted.sort();
        TranslationalEquivalence {
            pattern: pattern_sorted,
            translators,
            sub_tecs: sub_tecs.unwrap_or_else(Vec::new),
        }
    }

    /// Covered set = pattern ∪ all translated copies.
    #[getter]
    pub fn coverage(&self, _py: Python) -> PyResult<HashSet<(i64, i64)>> {
        let mut cov = HashSet::new();
        // Insert pattern points as i64
        for &(x, y) in &self.pattern {
            cov.insert((x as i64, y as i64));
        }
        // Insert translated copies
        for &(dx, dy) in &self.translators {
            for &(x, y) in &self.pattern {
                cov.insert((x as i64 + dx as i64, y as i64 + dy as i64));
            }
        }
        Ok(cov)
    }

    /// Compression ratio = |covered set| / (|pattern| + |translators|).
    #[getter]
    pub fn compression_ratio(&self, py: Python) -> PyResult<f64> {
        let covered_len = self.coverage(py)?.len() as f64;
        let pattern_len = self.pattern.len() as f64;
        let trans_len = self.translators.len() as f64;
        let denom = pattern_len + trans_len;
        if denom == 0.0 {
            Ok(0.0)
        } else {
            Ok(covered_len / denom)
        }
    }

    /// Bounding‑box compactness: |pattern| / (number of dataset points inside pattern's bbox).
    pub fn compactness(&self, points: HashSet<(i64, i64)>) -> f64 {
        if self.pattern.is_empty() {
            return 0.0;
        }
        // Convert pattern coordinates to i64 for bounds
        let xs: Vec<i64> = self.pattern.iter().map(|p| p.0 as i64).collect();
        let ys: Vec<i64> = self.pattern.iter().map(|p| p.1 as i64).collect();
        let min_x = *xs.iter().min().unwrap();
        let max_x = *xs.iter().max().unwrap();
        let min_y = *ys.iter().min().unwrap();
        let max_y = *ys.iter().max().unwrap();
        let mut count = 0;
        for &(x, y) in &points {
            if x >= min_x && x <= max_x && y >= min_y && y <= max_y {
                count += 1;
            }
        }
        if count == 0 {
            0.0
        } else {
            self.pattern.len() as f64 / count as f64
        }
    }
}

impl fmt::Display for TranslationalEquivalence {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f, "TEC(pattern={:?}, translators={:?})", self.pattern, self.translators
        )
    }
}

/// Compare two TECs according to the rules in ISBETTERTEC.
/// Returns true if tec1 is better than tec2.
#[pyfunction]
pub fn is_better_tec(
    py: Python,
    tec1: &TranslationalEquivalence,
    tec2: &TranslationalEquivalence,
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