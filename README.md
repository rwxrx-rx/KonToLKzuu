# KonToLKzuu — Kernel & KSU Build Pipeline

CI/CD pipeline for building 4.14 non-GKI Android kernels (device family: `camellia` / MT6833, e.g. POCO M3 Pro 5G / Redmi Note 10 5G), with optional ReSukiSU + SUSFS 2.2.0 integration, entirely on GitHub Actions.

## What it builds

Each run can produce, in parallel:

- **vanilla** — plain kernel, no root, no SUSFS.
- **resukisu_susfs** — ReSukiSU (KernelSU fork) + SUSFS 2.2.0, built and hook-integrated into the kernel source at build time.

Plus optional feature injectors applied to either variant: Baseband-Guard, WireGuard, F2FS backport, ZRAM/ZSTD, TCP BBR, TTL spoofing, ThinLTO/-O3.

## Repo layout

```
.github/
├── workflows/            # main.yml (entry point), build-kernel.yml (reusable), etc.
├── actions/              # setup-ksu, apply-susfs, inject-features, package-anykernel, download-toolchain
├── scripts/              # build_kernel.sh, hook injectors, contract validators, ksud bootstrap
├── manifest/             # one repo manifest XML per supported kernel source
└── hook-profiles.json    # manifest_name -> SUSFS hook profile mapping (see below)
patches/
├── camellia_v7_full_defconfig
├── camellia-anykernel/           # AnyKernel3 flashable ZIP template
└── susfs_v220/profiles/<name>/tree/   # pre-merged SUSFS 2.2.0 source tree per hook profile
```

## How ReSukiSU + SUSFS integration works

SUSFS on a legacy 4.14 kernel needs real source-level hook call-sites (not just a config flag), and those call-sites depend on the exact shape of the kernel source they're inserted into. This pipeline doesn't fuzzy-patch — it installs a pre-merged, known-good tree and validates it byte-for-byte.

Because of that, `resukisu_susfs` is only available for manifests that have a matching **hook profile** registered in `.github/hook-profiles.json`:

```json
{
  "camellia": "camellia-4.14",
  "lineage-23.2": "camellia-4.14"
}
```

- `manifest_name` not in this file → `build_variant=resukisu_susfs`/`both` is rejected immediately by `validate-inputs`, with the list of currently supported manifests.
- Every hook injection / validation step is fail-closed and exact-match: if a manifest's source doesn't actually match its assigned profile, the build stops clearly at the "Apply SUSFS Patch & Configs" step — not with a confusing error deep inside kernel compilation.

**Adding a new manifest:**
- If it's a fork/branch of a kernel source already covered by an existing profile (same layout), just add `"<manifest_name>": "<existing-profile>"` to `hook-profiles.json`.
- If it's a genuinely different kernel source/version, create `patches/susfs_v220/profiles/<new-profile>/tree/` with your own 3-way-merged SUSFS tree for that source, then register it the same way.

## Toolchain note

`toolchain=clang-22` pairs a modern LLVM/Clang with a very old (GCC 4.9-era) prebuilt binutils assembler used only for `CROSS_COMPILE`. `build_kernel.sh` forces `-fintegrated-as` so Clang assembles with its own backend instead of that ancient external `as`, avoiding assembler-syntax mismatches.

## Running a build

1. Fork this repo.
2. Actions → **Build Kernel & Tools (Automated Pipeline)** → Run workflow.
3. Pick `build_target`, `build_variant`, `manifest_name`, toolchain, and feature toggles.
4. Artifacts (flashable AnyKernel3 ZIP(s), Manager APK for the ReSukiSU leg) are uploaded to the run and to Releases.

The kernel source itself is not vendored here — it's pulled per-manifest via `.github/manifest/<name>.xml`.

## Credits

[`camellia-devs`](https://github.com/camellia-devs/kernel_xiaomi_mt6833) • [`LinuxxPU`](https://github.com/ahmad24shargh/LinuxxPU) • [`GKI_KernelSU_SUSFS`](https://github.com/WildKernels/GKI_KernelSU_SUSFS) • [`TheWildJames`](https://github.com/TheWildJames) • [`SUKISU`](https://github.com/ShirkNeko) • [`xxKSU`](https://github.com/backslashxx) • [`KernelSU`](https://github.com/tiann/KernelSU) • [`ReSukiSU`](https://github.com/ReSukiSU/ReSukiSU) • [`AnyKernel3`](https://github.com/osm0sis/AnyKernel3) • [`Baseband-guard`](https://github.com/vc-teahouse/Baseband-guard)

---

⚠️ Flashing a custom kernel carries risk (bootloop / data loss). Keep a backup and a way back to stock. Provided as-is, use at your own risk.
