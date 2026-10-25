from src.database import get_db

FATURAMENTO_ACIMA_DE_10000 = 10000
DESCONTO_ACIMA_DE_10000 = 0.1
FATURAMENTO_ACIMA_DE_5000 = 5000
DESCONTO_ACIMA_DE_5000 = 0.05
FATURAMENTO_ACIMA_DE_1000 = 1000
DESCONTO_ACIMA_DE_1000 = 0.02


def relatorio_vendas():
    row = get_db().execute(
        """
        SELECT
            COUNT(*) AS total_pedidos,
            COALESCE(SUM(total), 0) AS faturamento,
            COALESCE(SUM(CASE WHEN status = 'pendente' THEN 1 ELSE 0 END), 0) AS pendentes,
            COALESCE(SUM(CASE WHEN status = 'aprovado' THEN 1 ELSE 0 END), 0) AS aprovados,
            COALESCE(SUM(CASE WHEN status = 'cancelado' THEN 1 ELSE 0 END), 0) AS cancelados
        FROM pedidos
        """
    ).fetchone()
    total_pedidos = row["total_pedidos"]
    faturamento = row["faturamento"]
    desconto = _desconto(faturamento)
    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": row["pendentes"],
        "pedidos_aprovados": row["aprovados"],
        "pedidos_cancelados": row["cancelados"],
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }


def _desconto(faturamento):
    if faturamento > FATURAMENTO_ACIMA_DE_10000:
        return faturamento * DESCONTO_ACIMA_DE_10000
    if faturamento > FATURAMENTO_ACIMA_DE_5000:
        return faturamento * DESCONTO_ACIMA_DE_5000
    if faturamento > FATURAMENTO_ACIMA_DE_1000:
        return faturamento * DESCONTO_ACIMA_DE_1000
    return 0
