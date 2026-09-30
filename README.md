# FluoriteGraph

**FluoriteGraph** — невелика Python-бібліотека для опису **типізованого графа знань** для редактора Fluorite.
Вона дозволяє описувати сутності проєкту (файли, класи, методи тощо), зв'язки між ними
(«імпортує», «використовує» тощо) і групувати їх за допомогою гіперребер.

> Статус: рання версія `0.1.0`, API ще змінюється.

---

## Основна ідея

Звичайний граф — це просто множина вузлів і ребер. У FluoriteGraph і вузли, і ребра **мають тип**:

- **Тип вузлів** (`NodeType`) — це «категорія» сутностей, наприклад `файли`, `класи`, `методи`.
  Кожен тип містить свої вузли (`NodeType.Node`).
- **Тип ребер** (`EdgeType`) — це «вид» зв'язку, наприклад `імпортує` чи `використовує`.
  Тип визначає, чи є зв'язок напрямленим (`directed`), і містить конкретні ребра (`EdgeType.Edge`).
- **Гіперребра** (`HyperedgeType`) — системний тип: словник `id гіперребра → множина id дітей`.
  Дітьми можуть бути вершини або інші гіперребра, вкладеність завжди лишається DAG.
  Це технічна частина моделі, окремо вона не зображується.
- **Граф** (`FluoriteGraph`) — контейнер, що об'єднує всі типи вузлів, типи ребер і гіперребра.

```
FluoriteGraph
├── nodes:   {name: NodeType}     ← категорії вузлів
│              └── nodes: {id: Node}
├── edges:   {name: EdgeType}     ← категорії зв'язків
│              └── edges: {id: Edge(node_in → node_out)}
└── hyperedges: HyperedgeType     ← системний тип груп
               ├── hyperedges: {id: Hyperedge}
               └── children:   {id: {id дітей}}
```

Завдяки цьому одна й та сама пара вузлів може бути з'єднана кількома різними за змістом зв'язками,
а вузли різних категорій зберігаються окремо, але можуть вільно з'єднуватися між собою.

---

## Структура проєкту

| Файл               | Призначення                                                        |
|--------------------|--------------------------------------------------------------------|
| `FluoriteGraph.py` | Уся модель даних: `NodeType`, `EdgeType`, `HyperedgeType`, `FluoriteGraph` |
| `main.py`          | Демонстраційний приклад використання                               |
| `pyproject.toml`   | Метадані проєкту та залежності                                     |
| `uv.lock`          | Зафіксовані версії залежностей (для [uv](https://docs.astral.sh/uv/)) |

---

## Встановлення та запуск

Потрібен **Python 3.13+**. Проєкт керується через `uv`:

```bash
uv sync             # створити .venv і встановити залежності
uv run python main.py
```

Залежності:

- [`rich`](https://github.com/Textualize/rich) — гарний вивід структур у терміналі (використовується в `main.py`).

---

## API

### Ідентифікатори

Усі сутності (вузли, ребра, гіперребра) отримують числовий `id` з **одного глобального лічильника** (`itertools.count(1)`).
Тобто ідентифікатори унікальні в межах усього процесу, а не лише всередині одного типу:
якщо створено 3 вузли, то наступне ребро отримає `id = 4`.

### `NodeType`

```python
NodeType(name: str, nodes: dict[int, Node] = {})
```

Категорія вузлів.

| Метод                           | Опис |
|---------------------------------|------|
| `append(name, description=None)` | Створює вузол із заданим іменем та (необов'язковим) описом і додає його в тип. |
| `extend(nodes)`                  | Додає кілька вузлів. Кожен елемент — або рядок `"name"`, або пара `("name", "description")`. Інакше — `ValueError`. |
| `types[name]` (`__getitem__`)    | Пошук вузла за іменем. Повертає **один вузол**, якщо знайдено рівно один; **список**, якщо таких кілька; кидає `KeyError`, якщо не знайдено. |

#### `NodeType.Node`

Незмінний (`frozen`) dataclass:

| Поле          | Тип          | Опис |
|---------------|--------------|------|
| `name`        | `str`        | Ім'я вузла (не обов'язково унікальне) |
| `description` | `str \| None` | Опис |
| `node_id`     | `int`        | Автоматично присвоюється з глобального лічильника |

Оскільки вузол `frozen`, він хешується і може використовуватися як ключ словника чи елемент множини.

### `EdgeType`

```python
EdgeType(name: str, directed: bool = False, edges: dict[int, Edge] = {})
```

Категорія зв'язків. Прапорець `directed` визначає, чи має зв'язок напрям (`node_in → node_out`).

| Метод                          | Опис |
|--------------------------------|------|
| `append(node_in, node_out)`    | Створює ребро між двома вузлами і додає його в тип. |
| `extend(edges)`                | Додає кілька ребер: готові `Edge` або пари `(node_in, node_out)`. ⚠️ Див. «Відомі проблеми». |

#### `EdgeType.Edge`

Незмінний dataclass:

| Поле          | Тип             | Опис |
|---------------|-----------------|------|
| `node_in`     | `NodeType.Node` | Початковий вузол |
| `node_out`    | `NodeType.Node` | Кінцевий вузол |
| `description` | `str \| None`   | Опис ребра |
| `edge_id`     | `int`           | Автоматичний ідентифікатор |

### `HyperedgeType`

```python
HyperedgeType(
    hyperedges: dict[int, Hyperedge] = {},   # id → саме гіперребро
    children:   dict[int, set[int]]  = {},   # id → множина id дітей
)
```

Системний тип для гіперребер. Гіперребро — окрема сутність із власним `id`, а не вершина.
Діти — це вершини або інші гіперребра, тому гіперребра можна вкладати одне в одне.
Одна дитина може належати кільком гіперребрам.

Гіперребра — це службові позначки: теги, групування для редактора, результати аналізу, робочі набори.
Якщо про групу хочеться щось сказати (у неї є власні дані, вона бере участь у ребрах, її члени мають
різні ролі), її варто моделювати вершиною з `NodeType`, а не гіперребром.

#### `HyperedgeType.Hyperedge`

Незмінний dataclass:

| Поле           | Тип          | Опис |
|----------------|--------------|------|
| `name`         | `str`        | Назва гіперребра |
| `description`  | `str \| None` | Опис |
| `hyperedge_id` | `int`        | Автоматично присвоюється з глобального лічильника |

| Метод                         | Опис |
|-------------------------------|------|
| `append(hyperedge)`           | Реєструє гіперребро з порожньою множиною дітей. У графі це робить `graph.hyperadd(hyperedge)`. |
| `add(hyperedge_id, child_id)` | Додає дитину в зареєстроване гіперребро. Якщо дитина збігається з гіперребром або з неї можна дійти до гіперребра через вкладені гіперребра, кидає `ValueError`: так вкладеність завжди лишається DAG. |

Перевірка на цикли спрацьовує **лише в `add`**. Якщо змінювати `children` напряму
(`children[h].add(c)`, `children[h] = {...}`), перевірку буде обійдено, і відповідальність за DAG лягає на того, хто так робить.

Перевірка обходить у глибину лише гіперребра (вершини завжди листки), тому її вартість
пропорційна розміру піддерева дитини.

```python
monitoring = HyperedgeType.Hyperedge("під моніторингом")
graph.hyperadd(monitoring)
graph.hyperedges.add(monitoring.hyperedge_id, client.node_id)
```

### `FluoriteGraph`

```python
FluoriteGraph(
    nodes:   dict[str, NodeType] = {},
    edges:   dict[str, EdgeType] = {},
    hyperedges: HyperedgeType    = HyperedgeType(),
)
```

Кореневий контейнер. Гіперребра додаються через `hyperadd(hyperedge)`. Усе зберігається у словниках:

| Що                              | Ключ   | Доступ |
|---------------------------------|--------|--------|
| Типи вузлів / ребер (`graph.nodes`, `graph.edges`) | `name` | `graph.nodes["файли"]` — O(1) |
| Вузли, ребра (`NodeType.nodes`, `EdgeType.edges`)   | `id`   | `files.nodes[1]` — O(1) |
| Гіперребра, їхні діти (`graph.hyperedges.hyperedges`, `.children`) | `id` | `graph.hyperedges.children[9]` — O(1) |

Пошук вузла **за іменем** (`files["hello.py"]`) — це лінійний перебір, O(n). Це свідомий компроміс:
окремий індекс за іменем не зберігається, щоб економити пам'ять.

У конструктор можна передати як словники, так і звичайні списки — у `__post_init__` списки
автоматично перетворюються на словники за `name`. Якщо два типи
мають однакове ім'я, у словнику залишиться останній.

---

## Приклад

Приклад із `main.py` моделює невеликий Python-проєкт:

```python
from rich import print
from FluoriteGraph import FluoriteGraph, NodeType, EdgeType

# Типи вузлів
files = NodeType("файли")
files.extend(["hello.py", "myclass.py", "exec.py"])

classes = NodeType("класси")
classes.append("MyClass")

methods = NodeType("методи")
methods.extend(["method1", "method2"])

# Типи зв'язків
imports = EdgeType("імпортує", directed=True)
uses = EdgeType("використовує", directed=True)

imports.append(files["hello.py"], files["myclass.py"])   # hello.py → myclass.py
uses.append(files["hello.py"], methods["method1"])       # hello.py → method1

# Граф
graph = FluoriteGraph(
    nodes=[files, classes, methods],
    edges=[imports, uses],
)
print(graph)
```

Вивід (скорочено):

```
FluoriteGraph(
    nodes={
        'файли': NodeType(name='файли', nodes={1: Node(name='hello.py'), 2: Node(name='myclass.py'), 3: Node(name='exec.py')}),
        'класси': NodeType(name='класси', nodes={4: Node(name='MyClass')}),
        'методи': NodeType(name='методи', nodes={5: Node(name='method1'), 6: Node(name='method2')})
    },
    edges={
        'імпортує': EdgeType(name='імпортує', directed=True,
                 edges={7: Edge(node_in=Node(name='hello.py'), node_out=Node(name='myclass.py'))}),
        'використовує': EdgeType(name='використовує', directed=True,
                 edges={8: Edge(node_in=Node(name='hello.py'), node_out=Node(name='method1'))})
    },
    hyperedges=HyperedgeType(hyperedges={}, children={})
)
```

Зверніть увагу: `id` вузлів (1–6) і ребер (7–8) ідуть однією послідовністю — це наслідок спільного лічильника.

---

## Відомі проблеми та TODO

Проєкт на ранній стадії, тому є кілька незавершених місць:

- **`EdgeType.extend` не працює**: параметр названо `nedges`, а в тілі використовується `edges`;
  також `Edge` має бути `self.Edge`. Виклик призведе до `NameError`.
- **`EdgeType.append` не приймає `description`**, хоча поле `Edge.description` існує.
- **`main.py` завершується з помилкою**: після `main()` блок «RESULT» не закоментований
  і виконується як код (`NameError: name 'Node' is not defined`).
- **`case_hard()` у `main.py`** використовує методи, яких ще немає у `FluoriteGraph`:
  `append`, `connect(..., description=..., directed=...)` і `__getitem__`. Це чернетка майбутнього API.
- **`NodeType.__getitem__`** повертає або вузол, або список — викликаючому коду доводиться перевіряти тип результату.
  (Лінійний перебір тут навмисний — див. `FluoriteGraph` вище.)

Ідеї для розвитку:

- методи на рівні `FluoriteGraph` для додавання вузлів/зв'язків і пошуку;
- алгоритми аналізу графа (шляхи, цикли, компоненти зв'язності);
- серіалізація (JSON) для обміну даними з редактором Fluorite;
- тести.
