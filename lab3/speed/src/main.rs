use rayon::prelude::*;
use rand::Rng;
use rand::rngs::SmallRng;
use rand::SeedableRng;
use serde::Serialize;
use std::fs::File;
use std::io::Write;
use std::time::Instant;
use indicatif::{ProgressBar, ProgressStyle};
use std::sync::Arc;

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
    samples: u64,
}

fn sample_k_sum_probability(K: u32, n_samples: u64) {
    let start_time = Instant::now();
    let max_val = 2u128.pow(K);
    let num_digits = ((max_val as f64).log10().floor() as usize) + 1;
    let vec_size = 9 * num_digits + 1;

    // Progress bar
    let pb = Arc::new(ProgressBar::new(n_samples));
    pb.set_style(
        ProgressStyle::with_template(
            "[{elapsed_precise}] {wide_bar:.cyan/blue} {pos}/{len} ({eta})",
        )
        .unwrap()
        .progress_chars("=>-"),
    );

    // Parallel sampling
    let result = (0..n_samples as usize)
        .into_par_iter()
        .with_min_len(100_000)
        .fold(
            || {
                let rng = SmallRng::from_entropy();
                (vec![0u128; vec_size], rng)
            },
            {
                let pb = pb.clone();
                move |(mut local_vec, mut rng): (Vec<u128>, SmallRng), _| {
                    let n = rng.gen_range(0..max_val);
                    let sum = digit_sum(n);
                    local_vec[sum] += 1;

                    pb.inc(1);
                    (local_vec, rng)
                }
            },
        )
        .map(|(vec, _)| vec)
        .reduce(
            || vec![0u128; vec_size],
            |mut a, b| {
                for i in 0..vec_size {
                    a[i] += b[i];
                }
                a
            },
        );

    pb.finish_with_message("Sampling complete");

    // Serialize results
    let output = Output {
        digit_sum_counts: result,
        samples: n_samples,
    };

    let json = serde_json::to_string_pretty(&output).unwrap();
    let filename = format!("digit_sum_sample_K{}_N{}.json", K, n_samples);
    let mut file = File::create(&filename).expect("Failed to create file");
    file.write_all(json.as_bytes())
        .expect("Failed to write file");

    println!(
        "Finished {} samples in {:.2?}. Output saved to {}.",
        n_samples,
        start_time.elapsed(),
        filename
    );
}

fn main() {
    sample_k_sum_probability(100, 100_000_000_000);
}
