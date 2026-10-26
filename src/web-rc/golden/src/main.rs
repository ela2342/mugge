//! web-rc-golden -- writes the bit-exact noise goldens for US-179 AC5c.
//!
//! generator.rs is compiled unchanged from signal-gen, so the goldens are
//! what the Pi's signal-gen produces. The browser port of the generator is
//! tested against these files.
//!
//! Usage: web-rc-golden <output-dir>
//!
//! Writes one raw little-endian f32 file per (signal, seed, level) case,
//! named `<signal>_seed<seed>_level<level>.f32le`, holding the first
//! GOLDEN_SAMPLES mono samples.

#[allow(dead_code)]
#[path = "../../../signal-gen/src/generator.rs"]
mod generator;

use generator::{PinkNoiseGenerator, SignalGenerator, WhiteNoiseGenerator};
use std::fs;
use std::path::Path;
use std::process::ExitCode;

const GOLDEN_SAMPLES: usize = 4096;
const SEEDS: [u64; 3] = [0, 1, 174];
const LEVELS: [(f32, &str); 2] = [(1.0, "1.0"), (0.1, "0.1")];

fn render(gen: &mut dyn SignalGenerator, level: f32) -> Vec<f32> {
    let mut buf = vec![0.0f32; GOLDEN_SAMPLES];
    gen.generate(&mut buf, GOLDEN_SAMPLES, 1, 0x01, level);
    buf
}

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 2 {
        eprintln!("usage: {} <output-dir>", args[0]);
        return ExitCode::from(2);
    }
    let out = Path::new(&args[1]);
    if let Err(e) = fs::create_dir_all(out) {
        eprintln!("cannot create {}: {e}", out.display());
        return ExitCode::FAILURE;
    }

    for seed in SEEDS {
        for (level, level_name) in LEVELS {
            let cases: [(&str, Box<dyn SignalGenerator>); 2] = [
                ("white", Box::new(WhiteNoiseGenerator::new(seed))),
                ("pink", Box::new(PinkNoiseGenerator::new(seed))),
            ];
            for (signal, mut gen) in cases {
                let samples = render(gen.as_mut(), level);
                let bytes: Vec<u8> = samples.iter().flat_map(|s| s.to_le_bytes()).collect();
                let path = out.join(format!("{signal}_seed{seed}_level{level_name}.f32le"));
                if let Err(e) = fs::write(&path, &bytes) {
                    eprintln!("cannot write {}: {e}", path.display());
                    return ExitCode::FAILURE;
                }
                println!("{}", path.display());
            }
        }
    }
    ExitCode::SUCCESS
}
