// benches/siatec_benchmark.rs
use criterion::{criterion_group, criterion_main, BenchmarkId, Criterion, Throughput};
use _core::siatec::build_tecs_from_mtps;
use _core::sweepline::build_tecs_from_mtps as build_tecs_from_mtps_sweepline;
use std::time::Duration;

mod common;

fn bench_siatec(c: &mut Criterion) {
    let dataset = common::load_dataset();
    let n = dataset.len();

    let mut group = c.benchmark_group("SIATEC_algorithms");
    group.measurement_time(Duration::from_secs(10));
    group.sample_size(10);
    group.throughput(Throughput::Elements(n as u64));

    // Benchmark 1: Original SIATEC (hashmap SIA + naive translator enumeration)
    group.bench_with_input(BenchmarkId::new("hashmap_naive", n), &dataset, |b, data| {
        b.iter(|| build_tecs_from_mtps(data, false))
    });

    // Benchmark 2: Sweepline SIATEC (sweepline SIA + sweepline exact match)
    group.bench_with_input(BenchmarkId::new("sweepline_optimized", n), &dataset, |b, data| {
        // The dataset must be sorted – the sweepline internals assume sorted input.
        b.iter(|| build_tecs_from_mtps_sweepline(data, false))
    });

    group.finish();
}

criterion_group!(benches, bench_siatec);
criterion_main!(benches);