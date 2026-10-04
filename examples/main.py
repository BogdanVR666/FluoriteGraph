from rich import print

from fluoritegraph import FluoriteGraph, NodeType, EdgeType, Hyperedge

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

    olena = clients["Олена Шевчук"].node_id
    koval_1, koval_2 = (node.node_id for node in clients["Олександр Коваль"])  # тезки -> список
    ihor = clients["Ігор Мельник"].node_id
    romashka = clients["ТОВ Ромашка"].node_id

    # --- ребра ---
    owns = EdgeType("володіє", directed=True)
    owns.extend([
        (olena, accounts["UA11 ...0001"].node_id),
        (olena, accounts["UA11 ...0002"].node_id),
        (koval_1, accounts["UA22 ...0003"].node_id),
        (koval_2, accounts["UA33 ...0004"].node_id),
        (ihor, accounts["UA44 ...0005"].node_id),
        (romashka, accounts["UA55 ...0006"].node_id),
        (romashka, accounts["UA55 ...0007"].node_id),
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
        tx = transactions[tx].node_id
        pays.append(accounts[payer].node_id, tx)
        receives.append(tx, accounts[payee].node_id)
        at.append(tx, shops[shop].node_id)
        for item in items:
            contains.append(tx, goods[item].node_id)

    sells = EdgeType("продає", directed=True)
    for shop in ("АТБ №112", "АТБ №487"):
        sells.extend([(shops[shop].node_id, goods["Хліб"].node_id),
                      (shops[shop].node_id, goods["Молоко"].node_id)])
    sells.extend([(shops["Rozetka"].node_id, goods["iPhone 15"].node_id),
                  (shops["Rozetka"].node_id, goods["Подарункова картка 5000"].node_id)])

    related = EdgeType("пов'язані")  # ненапрямлене: родичі, спільна адреса тощо
    related.append(koval_2, ihor)

    # належність до мережі - предметний факт, тому ребро
    in_chain = EdgeType("входить у мережу", directed=True)  # магазин -> мережа
    in_chain.extend([
        (shops["АТБ №112"].node_id, chains["АТБ-Маркет"].node_id),
        (shops["АТБ №487"].node_id, chains["АТБ-Маркет"].node_id),
    ])

    part_of = EdgeType("частина схеми", directed=True)  # транзакція -> схема
    part_of.extend([
        (transactions[tx].node_id, schemes["Дроблення 3 x 5000"].node_id) for tx in ("T-004", "T-005", "T-006")
    ])

    organized = EdgeType("організував", directed=True)  # клієнт -> схема
    organized.append(koval_2, schemes["Дроблення 3 x 5000"].node_id)

    # ролі у справі - окремі типи ребер
    suspect = EdgeType("підозрюваний", directed=True)  # клієнт -> справа
    suspect.extend([(koval_2, cases["Справа 17/26"].node_id), (ihor, cases["Справа 17/26"].node_id)])

    witness = EdgeType("свідок", directed=True)  # клієнт -> справа
    witness.append(romashka, cases["Справа 17/26"].node_id)

    concerns = EdgeType("стосується", directed=True)  # справа -> схема
    concerns.append(cases["Справа 17/26"].node_id, schemes["Дроблення 3 x 5000"].node_id)

    graph = FluoriteGraph(
        nodes=[clients, accounts, shops, goods, transactions, chains, schemes, cases],
        edges=[owns, pays, receives, contains, at, sells, related,
               in_chain, part_of, organized, suspect, witness, concerns],
    )

    # --- гіперребра ---
    # лише службові позначки без власних даних предметної області
    # гіперребра створюються як типи вершин і ребер, а потім додаються в граф
    monitoring = Hyperedge("під моніторингом", "фінмоніторинг")
    duplicates = Hyperedge("можливі дублі", "знайдено алгоритмом")
    splitting = Hyperedge("можливе дроблення", "знайдено алгоритмом")
    anomalies = Hyperedge("аномалії")
    workset = Hyperedge("вибірка аналітика", "2026-09-30")

    monitoring.extend([koval_2, ihor, accounts["UA33 ...0004"].node_id, accounts["UA44 ...0005"].node_id])
    duplicates.extend(transactions[tx].node_id for tx in ("T-001", "T-002"))
    splitting.extend(transactions[tx].node_id for tx in ("T-004", "T-005", "T-006"))

    # до hyperadd у гіперребра немає owner, тож вкладеність перевіряється при додаванні в граф
    graph.hyperextend([monitoring, duplicates, splitting, anomalies, workset])

    # вкладені гіперребра
    anomalies.append(duplicates.hyperedge_id)
    anomalies.append(splitting.hyperedge_id)

    # вибірка: вкладені гіперребра, вершини різних типів, і тег разом зі своїм членом
    workset.append(anomalies.hyperedge_id)
    workset.append(monitoring.hyperedge_id)
    workset.append(cases["Справа 17/26"].node_id)
    workset.append(accounts["UA55 ...0007"].node_id)

    # ромб: T-005 у вибірці і напряму, і через anomalies -> splitting - дозволено
    workset.append(transactions["T-005"].node_id)

    # вершина в кількох гіперребрах: T-004 і в splitting, і в monitoring
    monitoring.append(transactions["T-004"].node_id)

    # цикл: аномалії не можуть містити вибірку, яка вже містить аномалії
    try:
        anomalies.append(workset.hyperedge_id)
    except ValueError as error:
        print(error)

    # прямі зміни множини обходять перевірку - це на відповідальності користувача
    # splitting.children.add(workset.hyperedge_id)  # тихо створить цикл

    # гіперребра - субграфи, тож операції над ними - звичайні операції над множинами
    print(monitoring.children & splitting.children)  # під моніторингом і водночас у дробленні

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

    imports.append(files["hello.py"].node_id, files["myclass.py"].node_id)
    uses.append(files["hello.py"].node_id, methods["method1"].node_id)

    graph = FluoriteGraph(
        nodes=[files, classes, methods], 
        edges=[imports, uses], 
    )
    print(graph)

if __name__ == "__main__":
    case_bank()

