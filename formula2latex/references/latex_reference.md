# LaTeX数学公式参考指南

## 常用数学符号LaTeX写法

### 希腊字母
| 符号 | LaTeX | 符号 | LaTeX |
|------|-------|------|-------|
| α | `\alpha` | β | `\beta` |
| γ | `\gamma` | δ | `\delta` |
| ε | `\epsilon` | θ | `\theta` |
| λ | `\lambda` | μ | `\mu` |
| π | `\pi` | σ | `\sigma` |
| φ | `\phi` | ω | `\omega` |
| Γ | `\Gamma` | Δ | `\Delta` |
| Θ | `\Theta` | Σ | `\Sigma` |
| Φ | `\Phi` | Ω | `\Omega` |

### 运算符
| 符号 | LaTeX | 符号 | LaTeX |
|------|-------|------|-------|
| ∑ | `\sum` | ∏ | `\prod` |
| ∫ | `\int` | ∬ | `\iint` |
| ∂ | `\partial` | ∇ | `\nabla` |
| ∈ | `\in` | ∉ | `\notin` |
| ⊂ | `\subset` | ∪ | `\cup` |
| ∩ | `\cap` | ∅ | `\emptyset` |
| ∞ | `\infty` | ∀ | `\forall` |
| ∃ | `\exists` | ¬ | `\neg` |

### 关系符
| 符号 | LaTeX | 符号 | LaTeX |
|------|-------|------|-------|
| ≤ | `\leq` | ≥ | `\geq` |
| ≠ | `\neq` | ≈ | `\approx` |
| ≡ | `\equiv` | ≪ | `\ll` |
| ≫ | `\gg` | ∼ | `\sim` |
| ⊥ | `\perp` | ∥ | `\parallel` |

### 矩阵与括号
```latex
\begin{pmatrix}
a & b \\
c & d
\end{pmatrix}
\quad
\begin{bmatrix}
1 & 0 \\
0 & 1
\end{bmatrix}
```

### 多行公式
```latex
\begin{align}
E &= mc^2 \\
F &= ma
\end{align}
```

### 分段函数
```latex
f(x) = \begin{cases}
x^2, & x \geq 0 \\
0, & x < 0
\end{cases}
```

## 论文公式提取注意事项

1. **上下标** — 注意区分 `x_i` (下标) 和 `x^i` (上标)
2. **花体字母** — 集合用 `\mathcal{}`，复数用 `\mathbb{}`
3. **公式编号** — 论文中 `(1)`、`(2)` 等编号不应包含在LaTeX代码中
4. **多字符变量** — 如 "max" 应用 `\max` 而非 `max`
5. **括号** — 用 `\left(` 和 `\right)` 自动调节括号大小
