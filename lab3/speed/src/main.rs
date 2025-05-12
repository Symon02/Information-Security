use rayon::prelude::*;
use serde::Serialize;
use std::fs::File;
use std::io::Write;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::time::Instant;

fn digit_sum(mut n: u128) -> usize {
    let mut sum = 0;
    while n > 0 {
        sum += (n % 10) as usize;
        n /= 10;
    }
    sum
}

#[derive(Serialize)]
struct Output {
    digit_sum_counts: Vec<u128>,
}

fn k_sum_probability(K: u128) {
    let start_time = Instant::now();
    let max = 2u128.pow(K as u32);
    let counter = AtomicUsize::new(0);
    let progress_interval = 10_000_000;

    let max_num = 2u128.pow(K as u32) - 1;
    let num_digits = ((max_num as f64).log10().floor() as usize) + 1;
    let vec_size = 9 * num_digits + 1; // +1 just in case

    // Parallel computation
    let result = (0..max)
        .into_par_iter()
        .map_init(
            || vec![0u128; vec_size],
            |local_vec, k| {
                let sum = digit_sum(k);
                local_vec[sum] += 1;

                let count = counter.fetch_add(1, Ordering::Relaxed);
                if count % progress_interval == 0 {
                    let elapsed = start_time.elapsed().as_secs();
                    println!("Processed: {} (Elapsed: {}s)", count, elapsed);
                }

                local_vec.clone()
            },
        )
        .reduce(
            || vec![0u128; vec_size],
            |mut a, b| {
                for i in 0..vec_size {
                    a[i] += b[i];
                }
                a
            },
        );

    println!("Finished in {:.2?}", start_time.elapsed());

    // Serialize and save to JSON
    let output = Output {
        digit_sum_counts: result,
    };

    let json = serde_json::to_string_pretty(&output).unwrap();
    let mut file =
        File::create(format!("digit_sum_counts_{}.json", K)).expect("Failed to create file");
    file.write_all(json.as_bytes())
        .expect("Failed to write file");

    println!("Results saved to digit_sum_counts.json");
}

fn main() {
    k_sum_probability(18);
}
