## How to use:

```yaml
- name: clippy
  uses: servo/actions/cargo-annotation@main
  with:
    cargo-command: clippy --features '${{ matrix.features }}' --target '${{ matrix.platform.target }}'
    with-annotation: ${{ matrix.platform.target == 'x86_64-unknown-linux-gnu' && matrix.features == '' }}
```
