use std::collections::HashMap;

use pyo3::prelude::*;

use crate::sia::find_mtps as find_mtps_rs;
use crate::siatec::build_tecs_from_mtps as build_tecs_from_mtps_rs;
use crate::cosiatec::cosiatec_compress as cosiatec_compress_rs;
use crate::recursia::recursive_cosiatec_compress as recursive_cosiatec_compress_rs;
use crate::tec::TranslationalEquivalence;

/// Python wrapper for `find_mtps` (SIA algorithm).
#[pyfunction]
pub fn find_mtps(
    dataset: Vec<(u32, u32)>,
    restrict_dpitch_zero: bool,
) -> HashMap<(i32, i32), Vec<(u32, u32)>> {
    find_mtps_rs(&dataset, restrict_dpitch_zero)
}

/// Python wrapper for `build_tecs_from_mtps` (SIATEC algorithm).
#[pyfunction]
pub fn build_tecs_from_mtps(
    dataset: Vec<(u32, u32)>,
    restrict_dpitch_zero: bool,
) -> Vec<TranslationalEquivalence> {
    build_tecs_from_mtps_rs(&dataset, restrict_dpitch_zero)
}

/// Python wrapper for `cosiatec_compress` (COSIATEC algorithm).
#[pyfunction]
pub fn cosiatec_compress(
    dataset: Vec<(u32, u32)>,
    restrict_dpitch_zero: bool,
) -> Vec<TranslationalEquivalence> {
    cosiatec_compress_rs(&dataset, restrict_dpitch_zero)
}

/// Python wrapper for `recursive_cosiatec_compress` (RECURSIA on COSIATEC).
#[pyfunction]
pub fn recursive_cosiatec_compress(
    dataset: Vec<(u32, u32)>,
    restrict_dpitch_zero: bool,
    min_pattern_size: usize,
) -> Vec<TranslationalEquivalence> {
    recursive_cosiatec_compress_rs(&dataset, restrict_dpitch_zero, min_pattern_size)
}