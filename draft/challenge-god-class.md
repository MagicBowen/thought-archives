# 挑战“上帝类”

---

[toc]

<div style="page-break-after: always;"></div>

---

## 直面“上帝类”

<div align="center"><img src="images/God_Class2.png" width="60%"></div>

在软件开发中，“上帝类”（God Class）是一个常见的反模式，它指的是一个类承担了过多的责任，其成员属性和方法特别多，代码逻辑复杂，耦合在一起，变得过于庞大和复杂。

如下的`FemFsdPathGenerator`类为一个典型的上帝类, 该类包含了200+个私有成员函数和250+个私有成员变量。

```cpp
class FemFsdPathGenerator
{
public:
    // ...
private:
    // 200+ private member functions
    // ...
private:
    // 250+ private member variables
    // ...
};
```

上帝类为软件带来如下危害：

- 维护困难：上帝类由于规模庞大，类的内部的所有属性对所有成员方法来说都相当是全局变量，这相当于大量的方法围绕着大量的全局变量进行编程，这容易带来不恰当的代码耦合，导致软件很难阅读和理解，增加了维护的难度，难以添加新功能，代码可扩展性差。
- 测试困难：由于类过于复杂，处理的流程过多过长，导致类的单元测试变得复杂，很难保证测试的覆盖性和有效性。
- 协作困难：上帝类造成了多人在同一类上工作，不容易隔离代码变化和进行人员分工，容易产生代码冲突，影响团队协作效率。

上帝类大多是由于在设计阶段没有充分考虑软件的设计以及类的职责，在不断的开发过程中，新功能被不断添加到已有的类中，而没有进行适当的重构；长期为了快速实现功能而做出妥协，最终积累成为问题。

“冰冻三尺非一日之寒”，对上帝类的重构往往比较难一蹴而就。上帝类犹如希腊神话中的九头蛇海德拉（Hydra），传说中它拥有多个头颅，而且每当有一个头被斩断时，就会有两个新头长出来。在极为庞大且复杂的上帝类中，尝试解决一个问题往往会引发更多的问题，就像斩断九头蛇的一个头会导致更多头的出现一样。

在面对上帝类时，**一些简单的拆分虽然能够从度量数据上获得改观，但是往往治标不治本**。软件工程师的设计和实现能力并没有通过这样的重构得到提升，后续的开发很容易再次陷入类似的困境。而深度的重构往往需要大量的时间和精力，风险较大。

我们希望能像希腊英雄赫拉克勒斯（Hercules）在对付九头蛇时采取的策略一样，不仅要斩断头颅，还要烧灼伤口，以防止新头的生长。因此我们需要引入一些更有效的面向对象的设计和实现技巧来帮助我们，同时我们还需要一些安全的重构操作手法，让对上帝类的重构尽量可以迭代进行，可进可退，控制风险。

后文将以`FemFsdPathGenerator`类为例展开分析和重构，让我们穿上盔甲，带上装备，一起来挑战“上帝类”。

## 案例与根因分析

`FemFsdPathGenerator`之所以复杂，是因为虽然它是一个面向对象的`class`，但是它的设计和实现却是面向过程的。它就好比一个复杂的C语言功能模块，其public入口方法就犹如模块的对外接口，而其内部的成员方法和成员变量则是一系列的模块内函数和全局变量。

随着不断地往这个模块内部增加新功能，其内部的方法和全局变量就会越来越多，导致模块内部的代码逻辑越来越复杂，耦合度越来越高，维护成本越来越高。

而如果我们从面向对象的Class的角度来看，它和模块究竟有哪些不同？

首先，一个class除了和模块一样，有对外的public接口，有内部的方法和变量，还有一个重要的特性，那就是它有自己的生命周期。一个class的对象生命周期是由它内部数据的生命周期来决定的，具体是由对象的创建和销毁来决定的。这就决定了，我们究竟是把数据放到函数参数上，还是放到对象的成员变量上，还是放到外部的全局变量上，是有一定的规则和原则的。这个原则就是要看数据的生命周期和变化频率；

其次，一个class的方法和成员变量是有一定的内聚度的，它们是一起工作的，是一起变化的，是一起维护和被复用的。这就决定了，我们究竟是把方法放到一个class中，还是放到另一个class中，是有一定的规则和原则的。这个原则就是要看方法的调用关系和数据的依赖关系；

最后，class之间是有清晰的依赖关系设计的，这种依赖设计是有强弱的（组合、聚合和依赖）。不同class的对象之间的可访问性，需要遵循其class之间的依赖关系的约束，根据依赖关系的强弱，对象之间的可见性和可访问性是完全不同的。

因此，如果使用了class，但没有关注class内部数据与方法的内聚度，没有清晰的按照不同的数据生命周期和变化频率来组织对象，没有设计良好的class之间的依赖关系来看护对象的可见性和可访问性，那么class就会退化成一个复杂的面向过程的模块，在C++中就会表现成为一个上帝类。

那么对于一个已经退化成上帝类的class，我们应该如何进行重构呢？

从表面上看，我们需要对上帝类进行拆分，将其庞杂的内部方法和成员变量拆分到不同的class中，这样就可以将一个大的复杂的上帝类拆分成为多个小的简单的class，达到降低复杂度，提高内聚度、可维护性和可复用性的目的。

更进一步的，我们需要问，如何拆分？上帝类中的方法和成员变量应该拆分到哪些class中？这些class之间的依赖关系应该如何设计？这些class的对象数据生命周期如何设计？我们如何通过class之间的依赖关系来约束对象的可见性和可访问性？

## 重构的设计策略

### 过程与数据

### 避免“贫血对象”

### 上帝类分解策略

#### 转移私有方法

#### 转移私有属性

- 生命周期分析
- 变化频率分析

#### 职责拆分

- 复用粒度分析
- 变化一致性分析

## 安全重构技巧

### 建立基线

- 分支
- 测试工程与用例
- 性能极限
- 工程与工具

### 消除冗余代码

### 移动私有方法到参数对象

### 移动私有静态方法到匿名命名空间

### 移动私有方法到Utility类

### 先提炼方法再移动

### 移动私有属性到参数对象

### 建立上下文对象类

### 利用上下文对象消除过多参数

### 封装容器类

### 优化容器封装类的设计

当一个容器集合被封装在一个类中之后，客户可能会基于各种各样的目的，希望对容器进行各种操作。例如基于各种不同条件从容器中过滤出一个数据子集返回后使用。

如果我们将所有的客户操作都作为封装类的接口实现，则会导致接口数量过多，从而使类变得不稳定，甚至可能也会演变成所谓的‘上帝类’。

对于容器集合的封装类而言，客户需要返回的数据子集的语意是不明的，只有客户才知道它的用途。所以，如何对返回的数据子集如何进行处理也应该是客户的责任，不应该放到封装类中。

这种情况下，一种做法是为封装类提供查询接口，由客户自定义一个过滤条件，封装类根据客户定义的过滤条件，负责访问内部的具体容器，将符合条件的结果返回给客户。

如下示例中的`PointContainer`类，它封装了内部容器`std::vector<Point> points_`，对外提供了一个`getPointsByFilter`接口，接受一个`std::function<bool(const Point&)>`类型的过滤器，根据过滤器的条件，返回符合条件的`Point`对象集合。

下面的例子使用了`std::list`作为返回值，这里使用了 C++ 的 NRVO 优化(Named Return Value Optimization)，避免了返回值的拷贝。

C++的返回值优化通常称为（Return Value Optimization，RVO），它是编译器的一种优化技术，用以消除函数返回对象造成的临时对象拷贝，从而提高程序的效率。此处示例中`selectedPoints`临时对象是具名的，因为被称为（Named Return Value Optimization，NRVO），它适用于函数中有具名对象被作为返回值的情况。


```cpp
class PointContainer {
public:

    std::list<Point> GetPointsByFilter(std::function<bool(const Point&)> filter) const {
        std::list<Point> selectedPoints;
        for (const auto& point : points_) {
            if (filter(point)) {
                selectedPoints.push_back(point);
            }
        }
        return selectedPoints;
    }
    // Other functions...

private:
    std::vector<Point> points_;
};
```

在上面的示例中，我们遗留了一个问题，就是`GetPointsByFilter`的返回类型是一个未经封装的`std::list`类型，这似乎违反了我们前面说的不要直接用容器类型作为函数入参和出参的原则。
另外，我们对客户代码期待函数使用什么容器集合作为返回值类型是难以预期的，这里把所有容器类型都穷举一遍也是不现实的。

我们分析一下会发现，客户在拿到返回的数据子集容器后一定有自己的意图。如果我们让接口反映的是用户自己的意图，而不是数据子集容器类型这么具体的实现细节，那么数据子集将会变成一个无用的中间层。

那么怎么用接口直接表达客户的对数据子集的操作意图，而不是数据子集本身呢？我们可以借助 Visitor 模式。

对于上面的例子，我们可以修改代码为：

```cpp
struct PointVisitor 
{ 
  virtual void Visit(const Point& point) = 0; 
  virtual ~PointVisitor() {} 
};

class PointContainer {
public:

    void Accept(PointVisitor& visitor) const {
        for (const auto& point : points_) {
            visitor.Visit(point);
        }
    }
    // Other functions...

private:
    std::vector<Point> points_;
};
```

对于上面修改后的 `PointerContainer`，仍旧隐藏了内部的容器类型`std::vector<Point> points_`, 但却做到了和客户对内部容器的具体操作意图以及数据子集类型解耦了。

客户对于 `std::vector<Point> points_` 的每种过滤和处理的操作，只需要定义一个 `PointVisitor` 的子类（实现 `visit` 函数），然后传递给`PointContainer::Accept`函数即可。

```cpp
class CountingVisitor : public PointVisitor {
public:
    int GetCount() const {
        return count_;
    }
private:
    void Visit(const Point& point) override {
        if (Filter(point)) {
            ++count_;
        }
    }

private:
    bool Filter(const Point& point) const {
        // Filter conditions...
    }

private:
    int count_{0};
};
```

```cpp
PointContainer container;
//...
CountingVisitor visitor;
container.Accept(visitor);
std::cout << visitor.GetCount() << std::endl;
```

如上代码示例，客户需要一个能按照条件过滤`point`并对其进行计数，则实现一个类`CountingVisitor`继承`PointVisitor`，实现`Visit`函数即可。
使用的时候，客户只用把`CountingVisitor`的对象传递给`PointContainer::Accept`函数，就可完成对`Point`的过滤和计数。

通过这种方式，我们成功地将客户的操作意图与数据子集的具体实现解耦，避免了将容器类型直接用作函数参数的问题。

此外，为每种操作意图单独定义一个`Visitor`的子类，大大方便了扩展新操作意图的能力，且无需修改`PointContainer`的实现。这些`Visitor`的子类可以放在不同的文件中供客户代码进行共享和复用，这样也提高了代码的可维护性和可复用性。

### 面向性能的优化

- 选择更高效的容器类型
- 为计算结果建立缓存
- 优化容器遍历算法