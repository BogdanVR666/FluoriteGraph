from rich import print

from FluoriteGraph import FluoriteGraph, NodeType, EdgeType, HyperedgeType

def case_hard():
    guys = ["Alice", "Bob", "Jeff", "Steve", "Donald", "Anton"]
    office_workers = guys[:-2] + ["Bohdan"]

    graph = FluoriteGraph()

    for guy in guys:
        graph.append(guy)

    graph.connect(graph["Alice"], graph["Steve"], description="loves", directed=True)

    # TODO: Зробити складні зв'язки і комплексний випадок


def case_bank():
    # --- вершини ---
    clients = NodeType("клієнти")
    clients.extend([
        ("Олена Шевчук", "ІПН 3011122233"),
        ("Олександр Коваль", "ІПН 2899911100"),
        ("Олександр Коваль", "ІПН 3344455566"),  # повний тезка
        ("Ігор Мельник", "ІПН 3100022211"),
        "ТОВ Ромашка",                           # юрособа без опису
    ])

    accounts = NodeType("рахунки")
    accounts.extend([
        ("UA11 ...0001", "UAH"),
        ("UA11 ...0002", "USD"),
        ("UA22 ...0003", "UAH"),
        ("UA33 ...0004", "UAH"),
        ("UA44 ...0005", "UAH"),
        ("UA55 ...0006", "UAH"),  # рахунок магазину
        ("UA55 ...0007", "UAH"),  # рахунок магазину
    ])

    shops = NodeType("магазини")
    shops.extend([
        ("АТБ №112", "Київ, вул. Хрещатик 1"),
        ("АТБ №487", "Львів, пл. Ринок 5"),
        ("Rozetka", "онлайн"),
    ])

    goods = NodeType("товари")
    goods.extend([
        ("Хліб", "арт. 1001"),
        ("Молоко", "арт. 1002"),
        ("iPhone 15", "арт. 9001"),
        ("Подарункова картка 5000", "арт. 9500"),
    ])

    # транзакція - n-арне відношення (платник, отримувач, товари, сума, час),
    # тому вона вершина, а не ребро
    transactions = NodeType("транзакції")
    transactions.extend([
        ("T-001", "2026-09-01 10:15, 84.50 UAH"),
        ("T-002", "2026-09-01 10:17, 84.50 UAH"),   # дубль T-001?
        ("T-003", "2026-09-02 23:58, 52000 UAH"),
        ("T-004", "2026-09-03 00:04, 5000 UAH"),
        ("T-005", "2026-09-03 00:05, 5000 UAH"),
        ("T-006", "2026-09-03 00:07, 5000 UAH"),
    ])

    # мережі, схеми і справи мають власні дані та беруть участь у ребрах,
    # тому це вершини, а не гіперребра
    chains = NodeType("мережі")
    chains.append("АТБ-Маркет", "мережа супермаркетів")

    schemes = NodeType("схеми")
    schemes.append("Дроблення 3 x 5000", "виявлена 2026-09-03")

    cases = NodeType("розслідування")
    cases.append("Справа 17/26", "підозра на дроблення платежів")

    olena = clients["Олена Шевчук"]
    koval_1, koval_2 = clients["Олександр Коваль"]  # тезки -> список
    ihor = clients["Ігор Мельник"]
    romashka = clients["ТОВ Ромашка"]

    # --- ребра ---
    owns = EdgeType("володіє", directed=True)
    owns.extend([
        (olena, accounts["UA11 ...0001"]),
        (olena, accounts["UA11 ...0002"]),
        (koval_1, accounts["UA22 ...0003"]),
        (koval_2, accounts["UA33 ...0004"]),
        (ihor, accounts["UA44 ...0005"]),
        (romashka, accounts["UA55 ...0006"]),
        (romashka, accounts["UA55 ...0007"]),
    ])

    pays = EdgeType("платить", directed=True)      # рахунок -> транзакція
    receives = EdgeType("отримує", directed=True)  # транзакція -> рахунок
    contains = EdgeType("містить", directed=True)  # транзакція -> товар
    at = EdgeType("в магазині", directed=True)     # транзакція -> магазин

    for tx, payer, payee, shop, items in [
        ("T-001", "UA11 ...0001", "UA55 ...0006", "АТБ №112", ["Хліб", "Молоко"]),
        ("T-002", "UA11 ...0001", "UA55 ...0006", "АТБ №112", ["Хліб", "Молоко"]),
        ("T-003", "UA22 ...0003", "UA55 ...0007", "Rozetka", ["iPhone 15"]),
        ("T-004", "UA33 ...0004", "UA55 ...0007", "Rozetka", ["Подарункова картка 5000"]),
        ("T-005", "UA33 ...0004", "UA55 ...0007", "Rozetka", ["Подарункова картка 5000"]),
        ("T-006", "UA44 ...0005", "UA55 ...0007", "Rozetka", ["Подарункова картка 5000"]),
    ]:
        tx = transactions[tx]
        pays.append(accounts[payer], tx)
        receives.append(tx, accounts[payee])
        at.append(tx, shops[shop])
        for item in items:
            contains.append(tx, goods[item])

    sells = EdgeType("продає", directed=True)
    for shop in ("АТБ №112", "АТБ №487"):
        sells.extend([(shops[shop], goods["Хліб"]), (shops[shop], goods["Молоко"])])
    sells.extend([(shops["Rozetka"], goods["iPhone 15"]),
                  (shops["Rozetka"], goods["Подарункова картка 5000"])])

    related = EdgeType("пов'язані")  # ненапрямлене: родичі, спільна адреса тощо
    related.append(koval_2, ihor)

    # належність до мережі - предметний факт, тому ребро
    in_chain = EdgeType("входить у мережу", directed=True)  # магазин -> мережа
    in_chain.extend([
        (shops["АТБ №112"], chains["АТБ-Маркет"]),
        (shops["АТБ №487"], chains["АТБ-Маркет"]),
    ])

    part_of = EdgeType("частина схеми", directed=True)  # транзакція -> схема
    part_of.extend([
        (transactions[tx], schemes["Дроблення 3 x 5000"]) for tx in ("T-004", "T-005", "T-006")
    ])

    organized = EdgeType("організував", directed=True)  # клієнт -> схема
    organized.append(koval_2, schemes["Дроблення 3 x 5000"])

    # ролі у справі - окремі типи ребер
    suspect = EdgeType("підозрюваний", directed=True)  # клієнт -> справа
    suspect.extend([(koval_2, cases["Справа 17/26"]), (ihor, cases["Справа 17/26"])])

    witness = EdgeType("свідок", directed=True)  # клієнт -> справа
    witness.append(romashka, cases["Справа 17/26"])

    concerns = EdgeType("стосується", directed=True)  # справа -> схема
    concerns.append(cases["Справа 17/26"], schemes["Дроблення 3 x 5000"])

    graph = FluoriteGraph(
        nodes=[clients, accounts, shops, goods, transactions, chains, schemes, cases],
        edges=[owns, pays, receives, contains, at, sells, related,
               in_chain, part_of, organized, suspect, witness, concerns],
    )

    # --- гіперребра ---
    # лише службові позначки без власних даних предметної області
    monitoring = HyperedgeType.Hyperedge("під моніторингом", "фінмоніторинг")
    duplicates = HyperedgeType.Hyperedge("можливі дублі", "знайдено алгоритмом")
    splitting = HyperedgeType.Hyperedge("можливе дроблення", "знайдено алгоритмом")
    anomalies = HyperedgeType.Hyperedge("аномалії")
    workset = HyperedgeType.Hyperedge("вибірка аналітика", "2026-09-30")

    for hyperedge in (monitoring, duplicates, splitting, anomalies, workset):
        graph.hyperadd(hyperedge)

    graph.hyperedges.add(monitoring.hyperedge_id, koval_2.node_id)
    graph.hyperedges.add(monitoring.hyperedge_id, ihor.node_id)
    graph.hyperedges.add(monitoring.hyperedge_id, accounts["UA33 ...0004"].node_id)
    graph.hyperedges.add(monitoring.hyperedge_id, accounts["UA44 ...0005"].node_id)

    graph.hyperedges.add(duplicates.hyperedge_id, transactions["T-001"].node_id)
    graph.hyperedges.add(duplicates.hyperedge_id, transactions["T-002"].node_id)

    graph.hyperedges.add(splitting.hyperedge_id, transactions["T-004"].node_id)
    graph.hyperedges.add(splitting.hyperedge_id, transactions["T-005"].node_id)
    graph.hyperedges.add(splitting.hyperedge_id, transactions["T-006"].node_id)

    # вкладені гіперребра
    graph.hyperedges.add(anomalies.hyperedge_id, duplicates.hyperedge_id)
    graph.hyperedges.add(anomalies.hyperedge_id, splitting.hyperedge_id)

    # вибірка: вкладене гіперребро, вершини різних типів, і тег разом зі своїм членом
    graph.hyperedges.add(workset.hyperedge_id, anomalies.hyperedge_id)
    graph.hyperedges.add(workset.hyperedge_id, monitoring.hyperedge_id)
    graph.hyperedges.add(workset.hyperedge_id, cases["Справа 17/26"].node_id)
    graph.hyperedges.add(workset.hyperedge_id, accounts["UA55 ...0007"].node_id)

    # ромб: T-005 у вибірці і напряму, і через anomalies -> splitting - дозволено
    graph.hyperedges.add(workset.hyperedge_id, transactions["T-005"].node_id)

    # вершина в кількох гіперребрах: T-004 і в splitting, і в monitoring
    graph.hyperedges.add(monitoring.hyperedge_id, transactions["T-004"].node_id)

    # цикл: аномалії не можуть містити вибірку, яка вже містить аномалії
    try:
        graph.hyperedges.add(anomalies.hyperedge_id, workset.hyperedge_id)
    except ValueError as error:
        print(error)

    print(graph)


def main():
    filenames = ["hello.py", "myclass.py", "exec.py"]
    
    files = NodeType("файли")
    files.extend(filenames)

    classes = NodeType("класси")
    classes.append("MyClass")

    method_names = ["method1", "method2"]    
    
    methods = NodeType("методи")
    methods.extend(method_names)

    imports = EdgeType("імпортує", directed=True)
    uses = EdgeType("використовує", directed=True)

    imports.append(files["hello.py"], files["myclass.py"])
    uses.append(files["hello.py"], methods["method1"])

    graph = FluoriteGraph(
        nodes=[files, classes, methods], 
        edges=[imports, uses], 
    )
    print(graph)

if __name__ == "__main__":
    case_bank()

