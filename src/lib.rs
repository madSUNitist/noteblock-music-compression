mod sia;
mod tec;
mod siatec;
mod cosiatec;
mod recursia;

mod wrapper;

use pyo3::prelude::*;
use wrapper::{
    find_mtps, 
    build_tecs_from_mtps, 
    cosiatec_compress, 
    recursive_cosiatec_compress
};

#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(find_mtps, m)?)?;
    m.add_function(wrap_pyfunction!(build_tecs_from_mtps, m)?)?;
    m.add_function(wrap_pyfunction!(cosiatec_compress, m)?)?;
    m.add_function(wrap_pyfunction!(recursive_cosiatec_compress, m)?)?;
    
    m.add_class::<tec::TranslationalEquivalence>()?;
    
    Ok(())
}