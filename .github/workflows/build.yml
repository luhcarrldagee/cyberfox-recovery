name: Build CyberFox recovery
on:
  workflow_dispatch:
    inputs:
      build_type:
        description: "Beta (adb + MTP on) or Stable"
        default: Beta
        type: choice
        options: [Beta, Stable]
permissions:
  contents: write
  issues: write
concurrency:
  group: cyberfox-build
  cancel-in-progress: false
jobs:
  build:
    runs-on: ubuntu-24.04
    timeout-minutes: 300
    steps:
      - name: Free disk space and add swap
        run: |
          df -h /
          sudo rm -rf /usr/share/dotnet /usr/local/lib/android /opt/ghc /usr/local/.ghcup \
            /opt/hostedtoolcache/CodeQL /usr/share/swift /usr/local/share/powershell \
            /usr/local/share/chromium /usr/local/lib/node_modules /opt/microsoft /opt/google || true
          sudo docker image prune --all --force >/dev/null 2>&1 || true
          sudo swapoff -a || true
          sudo rm -f /mnt/swapfile /swapfile

          sudo fallocate -l 24G /swapfile && sudo chmod 600 /swapfile
          sudo mkswap /swapfile >/dev/null && sudo swapon -p 10 /swapfile

          sudo modprobe zram || true
          if [ -e /sys/block/zram0 ]; then
            echo zstd | sudo tee /sys/block/zram0/comp_algorithm >/dev/null || true
            echo 12G  | sudo tee /sys/block/zram0/disksize >/dev/null
            sudo mkswap /dev/zram0 >/dev/null && sudo swapon -p 100 /dev/zram0
          fi
          sudo sysctl vm.swappiness=100 vm.vfs_cache_pressure=200

          sudo mkdir -p /home/runner/src && sudo chown runner:runner /home/runner/src
          df -h /; free -g; swapon --show
          avail=$(df --block-size=1G --output=avail / | tail -1)
          echo "Free on /: ${avail} GB"
          [ "$avail" -ge 75 ] || { echo "Not enough disk for a full sync and build"; exit 1; }

      - uses: actions/checkout@v4

      - name: Install build dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y git-core gnupg flex bison build-essential zip unzip curl zlib1g-dev \
            libc6-dev-i386 x11proto-core-dev libx11-dev lib32z1-dev libgl1-mesa-dev libxml2-utils \
            xsltproc fontconfig python3 python3-pip python-is-python3 python3-pil rsync bc lz4 cpio \
            libssl-dev ccache jq
          mkdir -p ~/bin
          curl -fsSL https://storage.googleapis.com/git-repo-downloads/repo -o ~/bin/repo
          chmod +x ~/bin/repo
          echo "$HOME/bin" >> "$GITHUB_PATH"
          git config --global user.name "CyberFox CI"
          git config --global user.email "ci@cyberfox.invalid"
          git config --global color.ui false
          df -h /home/runner/src; free -g; nproc

      - name: Sync and patch
        run: |
          set -o pipefail
          ( while true; do echo "[mon $(date -u +%H:%M)] $(df -h --output=avail /home/runner/src / | tail -2 | tr -s ' \n' ' ') mem: $(free -m | awk '/Mem/{print $7"MB avail"}') swap: $(free -m | awk '/Swap/{print $3"MB used"}')"; sleep 120; done ) &
          GH_TOKEN=${{ github.token }} bash tools/ci_monitor.sh sync.log "Sync" &
          bash tools/build.sh --top /home/runner/src/fox --sync --prepare 2>&1 | tee sync.log
          du -sh /home/runner/src/fox; df -h /home/runner/src

      - name: Compile
        run: |
          set -o pipefail
          ( while true; do echo "[mon $(date -u +%H:%M)] $(df -h --output=avail /home/runner/src / | tail -2 | tr -s ' \n' ' ') mem: $(free -m | awk '/Mem/{print $7"MB avail"}') swap: $(free -m | awk '/Swap/{print $3"MB used"}')"; sleep 120; done ) &
          GH_TOKEN=${{ github.token }} bash tools/ci_monitor.sh "$GITHUB_WORKSPACE/build.log" "Compile" &

          export GOGC=25
          export GOMEMLIMIT=10GiB
          export _JAVA_OPTIONS="-Xmx3g"
          export NINJA_ARGS="-j2"
          export ALLOW_MISSING_DEPENDENCIES=true

          cd /home/runner/src/fox/device/google/pixels
          nice -n 15 ./build.sh -n CyberFox --build-type "${{ inputs.build_type }}" --no-patches -j 2 2>&1 | tee "$GITHUB_WORKSPACE/build.log"

      - name: Memory diagnostics on failure
        if: failure() || cancelled()
        run: |
          free -h; swapon --show
          sudo dmesg | grep -i -E "out of memory|oom|killed process" | tail -20 || true

      - name: Collect artifacts
        run: |
          mkdir -p dist
          for f in /home/runner/src/fox/device/google/pixels/builds/OrangeFox-*-CyberFox-aio.*; do
            b="$(basename "$f")"; cp "$f" "dist/${b/OrangeFox-/CyberFox-}"
          done
          ls dist/CyberFox-* && (cd dist && sha256sum CyberFox-*-aio.* > SHA256SUMS-recovery)

      - name: Upload build log
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: build-log
          path: |
            sync.log
            build.log
            /home/runner/src/fox/out/error.log
          if-no-files-found: ignore

      - name: Upload recovery
        uses: actions/upload-artifact@v4
        with:
          name: cyberfox-recovery
          path: |
            dist/CyberFox-*
            dist/SHA256SUMS-recovery
          if-no-files-found: error

      - name: Publish release
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          bash tools/build_zips.sh
          (cd dist/zips && zip -q ../CyberFox-Lab-Tool-Zips.zip ./*.zip SHA256SUMS)
          tag="build-$(date -u +%Y%m%d-%H%M)"
          gh release create "$tag" dist/CyberFox-* dist/SHA256SUMS-recovery dist/CyberFox-Lab-Tool-Zips.zip \
            --title "CyberFox ${{ inputs.build_type }} $tag" \
            --notes "CyberFox Recovery for Pixel 6a (bluejay), built from OrangeFox fox_16.0 and leegarchat/twrp_device_google_pixels R12_16. Install with docs/INSTALL.md: unzip, run install-desktop.sh in fastboot, wait for RESULT: OK, then fastboot reboot recovery. Keep your stock vendor_boot.img for rollback."