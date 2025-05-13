#![allow(dead_code, non_snake_case)]

use num_bigint::BigUint;
use num_traits::Zero;
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
    samples: u128,
}

fn sample_k_sum_probability(K: u32) {
    let start_time = Instant::now();
    const FULL_ENUM_LIMIT: u128 = 100_000_000_000;

    let max_val = 1u128 << K;
    let num_digits = ((max_val as f64).log10().floor() as usize) + 1;
    let vec_size = 9 * num_digits + 1;

    let (digit_sum_counts, actual_samples): (Vec<u128>, u128) = if max_val <= FULL_ENUM_LIMIT {
        println!("Enumerating all {} values for K = {}", max_val, K);

        let pb = Arc::new(ProgressBar::new(max_val.try_into().unwrap()));
        pb.set_style(
            ProgressStyle::with_template(
                "[{elapsed_precise}] {wide_bar:.cyan/blue} {pos}/{len} ({eta})",
            )
            .unwrap()
            .progress_chars("=>-"),
        );

        let result = (0..max_val as usize)
            .into_par_iter()
            .with_min_len(100_000)
            .fold(
                || vec![0u128; vec_size],
                {
                    let pb = pb.clone();
                    move |mut local_vec: Vec<u128>, k| {
                        let sum = digit_sum(k as u128);
                        local_vec[sum] += 1;
                        pb.inc(1);
                        local_vec
                    }
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

        pb.finish_with_message("Full enumeration complete.");
        (result, max_val)
    } else {
        println!(
            "Falling back to random sampling for K = {} (sampling {} values)",
            K, FULL_ENUM_LIMIT
        );

        // let pb = Arc::new(ProgressBar::new(FULL_ENUM_LIMIT));
        // pb.set_style(
        //     ProgressStyle::with_template(
        //         "[{elapsed_precise}] {wide_bar:.cyan/blue} {pos}/{len} ({eta})",
        //     )
        //     .unwrap()
        //     .progress_chars("=>-"),
        // );

        let result = (0..FULL_ENUM_LIMIT as usize)
            .into_par_iter()
            .with_min_len(100_000)
            .fold(
                || {
                    let rng = SmallRng::from_entropy();
                    (vec![0u128; vec_size], rng)
                },
                {
                    // let pb = pb.clone();
                    move |(mut local_vec, mut rng): (Vec<u128>, SmallRng), _| {
                        let n = rng.gen_range(0..max_val);
                        let sum = digit_sum(n);
                        local_vec[sum] += 1;

                        // pb.inc(1);
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

        // pb.finish_with_message("Sampling complete.");
        (result, FULL_ENUM_LIMIT)
    };

    // Serialize results
    let output = Output {
        digit_sum_counts: digit_sum_counts,
        samples: actual_samples,
    };

    let json = serde_json::to_string_pretty(&output).unwrap();
    let filename = format!("digit_sum_sample_K{}_N{}.json", K, actual_samples);
    let mut file = File::create(&filename).expect("Failed to create file");
    file.write_all(json.as_bytes())
        .expect("Failed to write file");

    println!(
        "Finished {} samples in {:.2?}. Output saved to {}.",
        actual_samples,
        start_time.elapsed(),
        filename
    );
}

#[derive(Serialize)]
struct PeakResult {
    K: u32,
    most_frequent_sum: usize,
    count: u128,
}

fn random_kbit_biguint(K: u32, rng: &mut impl Rng) -> BigUint {
    let bits: String = (0..K)
        .map(|_| if rng.gen_bool(0.5) { '1' } else { '0' })
        .collect();
    BigUint::parse_bytes(bits.as_bytes(), 2).unwrap_or_else(BigUint::zero)
}

pub fn find_most_frequent_per_k(K_min: u32, K_max: u32, n_samples: usize) {
    let start_time = Instant::now();
    let mut results = Vec::new();

    for K in K_min..=K_max {
        println!("Processing K = {}", K);
        // Estimated maximum digit sum: max digit is 9, max decimal digits for 2^K ~ K * log10(2)
        let max_digits = (K as f64 * std::f64::consts::LOG10_2).ceil() as usize;
        let vec_size = 9 * max_digits + 1;

        let pb = Arc::new(ProgressBar::new(n_samples as u64));
        pb.set_style(
            ProgressStyle::with_template(
                "[{elapsed_precise}] {wide_bar:.cyan/blue} {msg} {pos}/{len} ({eta})",
            )
            .unwrap()
            .progress_chars("=>-"),
        );
        pb.set_message(format!("K = {}", K));

        let digit_sum_counts = (0..n_samples)
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
                        let n = random_kbit_biguint(K, &mut rng);
                        let sum = n
                            .to_string()
                            .chars()
                            .map(|c| c.to_digit(10).unwrap() as usize)
                            .sum::<usize>();
                        if sum < local_vec.len() {
                            local_vec[sum] += 1;
                        }
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

        pb.finish_with_message(format!("Done K = {}", K));

        // Find the peak
        let (max_index, &max_count) = digit_sum_counts
            .iter()
            .enumerate()
            .max_by_key(|&(_, count)| count)
            .unwrap();

        results.push(PeakResult {
            K,
            most_frequent_sum: max_index,
            count: max_count,
        });
    }

    // Serialize to JSON
    let json = serde_json::to_string_pretty(&results).unwrap();
    let filename = format!("peak_digit_sums_K{}_to_K{}.json", K_min, K_max);
    let mut file = File::create(&filename).expect("Failed to create file");
    file.write_all(json.as_bytes()).expect("Failed to write JSON");

    println!(
        "All done in {:.2?}. Results saved to {}",
        start_time.elapsed(),
        filename
    );
}

fn main() {
    sample_k_sum_probability(8);

    // find_most_frequent_per_k(100, 250, 100_000_000);
}
