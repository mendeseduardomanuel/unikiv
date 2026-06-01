"""
Teste do Cálculo de Self-Attention — Tarefa 34
Universidade Kimpa Vita · Grupo 02 · NLP & GenAI Capítulo V

Fórmula: Attention(Q, K, V) = softmax( Q × Kᵀ / √d_k ) × V
"""

import numpy as np

# ─────────────────────────────────────────────
# VALORES ESPERADOS (calculados manualmente na Tarefa 34)
# ─────────────────────────────────────────────
ESPERADO_SCORES = np.array([
    [1, 0, 1],
    [0, 1, 0],
    [1, 0, 1]
], dtype=float)

ESPERADO_SCORES_ESCALADOS = np.array([
    [0.707, 0.000, 0.707],
    [0.000, 0.707, 0.000],
    [0.707, 0.000, 0.707]
])

ESPERADO_ATENCAO = np.array([
    [0.401, 0.198, 0.401],
    [0.248, 0.504, 0.248],
    [0.401, 0.198, 0.401]
])

ESPERADO_OUTPUT = np.array([
    [0.802, 0.198],
    [0.496, 0.504],
    [0.802, 0.198]
])


# ─────────────────────────────────────────────
# IMPLEMENTAÇÃO DO SELF-ATTENTION
# ─────────────────────────────────────────────

def self_attention(Q, K, V):
    """
    Calcula um passo de Self-Attention.
    Retorna o output final e os resultados intermédios para inspecção.
    """
    d_k = Q.shape[1]

    # Passo 1: Scores = Q × Kᵀ
    scores = Q @ K.T

    # Passo 2: Escalar por √d_k
    scores_escalados = scores / np.sqrt(d_k)

    # Passo 3: Softmax linha a linha
    def softmax(x):
        e = np.exp(x - np.max(x))   # subtrai o max para estabilidade numérica
        return e / e.sum()

    pesos_atencao = np.array([softmax(linha) for linha in scores_escalados])

    # Passo 4: Output = pesos × V
    output = pesos_atencao @ V

    return output, scores, scores_escalados, pesos_atencao


# ─────────────────────────────────────────────
# FUNÇÕES DE TESTE
# ─────────────────────────────────────────────

def verificar(nome, obtido, esperado, tolerancia=1e-3):
    """Compara dois arrays e imprime o resultado do teste."""
    igual = np.allclose(obtido, esperado, atol=tolerancia)
    status = "✅ PASSOU" if igual else "❌ FALHOU"
    print(f"  {status}  {nome}")
    if not igual:
        print(f"           Obtido:   {obtido}")
        print(f"           Esperado: {esperado}")
    return igual


def testar_softmax_soma_um(pesos):
    """Verifica que cada linha da matriz de atenção soma 1."""
    somas = pesos.sum(axis=1)
    ok = np.allclose(somas, 1.0, atol=1e-6)
    status = "✅ PASSOU" if ok else "❌ FALHOU"
    print(f"  {status}  Softmax soma 1 em cada linha → {np.round(somas, 6)}")
    return ok


def testar_simetria(output):
    """Token 1 e Token 3 são idênticos → output deve ser igual."""
    ok = np.allclose(output[0], output[2], atol=1e-6)
    status = "✅ PASSOU" if ok else "❌ FALHOU"
    print(f"  {status}  Token 1 == Token 3 (simetria esperada)")
    return ok


def testar_token2_auto_atencao(pesos):
    """Token 2 deve prestar mais atenção a si próprio (diagonal > vizinhos)."""
    ok = pesos[1, 1] > pesos[1, 0]
    status = "✅ PASSOU" if ok else "❌ FALHOU"
    print(f"  {status}  Token 2 auto-atenção ({pesos[1,1]:.3f}) > atenção cruzada ({pesos[1,0]:.3f})")
    return ok


# ─────────────────────────────────────────────
# MAIN — EXECUTAR TODOS OS TESTES
# ─────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  TESTE DO SELF-ATTENTION — Tarefa 34")
    print("  NLP & GenAI · Universidade Kimpa Vita · Grupo 02")
    print("=" * 60)

    # Matrizes de entrada (Q = K = V = identidade 3×2)
    Q = K = V = np.array([
        [1, 0],
        [0, 1],
        [1, 0]
    ], dtype=float)

    print(f"\n  d_k = {Q.shape[1]}  |  Sequência: 3 tokens")
    print(f"  Q = K = V = matriz identidade 3×2\n")

    # Executar o Self-Attention
    output, scores, scores_esc, pesos = self_attention(Q, K, V)

    # ── Testes por passo ──────────────────────────────────
    print("── Passo 1: Q × Kᵀ (Scores) ──────────────────────────")
    r1 = verificar("Scores corretos", scores, ESPERADO_SCORES)

    print("\n── Passo 2: Escalar por √d_k ──────────────────────────")
    r2 = verificar("Scores escalados corretos", scores_esc, ESPERADO_SCORES_ESCALADOS, tolerancia=1e-2)

    print("\n── Passo 3: Softmax ────────────────────────────────────")
    r3 = verificar("Matriz de atenção correta", pesos, ESPERADO_ATENCAO, tolerancia=1e-2)
    r4 = testar_softmax_soma_um(pesos)

    print("\n── Passo 4: Output = pesos × V ─────────────────────────")
    r5 = verificar("Output final correto", output, ESPERADO_OUTPUT, tolerancia=1e-2)

    print("\n── Propriedades do resultado ───────────────────────────")
    r6 = testar_simetria(output)
    r7 = testar_token2_auto_atencao(pesos)

    # ── Resumo ────────────────────────────────────────────
    total = sum([r1, r2, r3, r4, r5, r6, r7])
    print("\n" + "=" * 60)
    print(f"  RESULTADO FINAL:  {total}/7 testes passaram")
    print("=" * 60)

    # ── Valores detalhados ────────────────────────────────
    print("\n📊 Valores calculados:")
    print(f"\n  Scores (Q × Kᵀ):\n{scores}")
    print(f"\n  Scores escalados (/ √{Q.shape[1]}):\n{np.round(scores_esc, 3)}")
    print(f"\n  Matriz de Atenção (softmax):\n{np.round(pesos, 3)}")
    print(f"\n  Output final:\n{np.round(output, 3)}")


if __name__ == "__main__":
    main()
