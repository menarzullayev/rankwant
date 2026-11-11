# Ma’lumotlar tuzilmasidan $O(T(n)\log n)$ vaqtda o‘chirish {#deleting-from-a-data-structure-in-otnlog-n}

Faraz qilaylik, sizda elementlarni **haqiqiy** $O(T(n))$ vaqtda qo‘shishga imkon beradigan ma’lumotlar tuzilmasi bor.
Ushbu maqolada o‘chirishni offline rejimda $O(T(n)\log n)$ vaqtda bajarishga imkon beradigan usul tasvirlanadi.

## Algoritm {#algorithm}

Har bir element ma’lumotlar tuzilmasida qo‘shilish va o‘chirilish orasidagi bir necha vaqt oralig‘ida “tirik” bo‘ladi.
Keling, so‘rovlar ustida segment daraxti quraylik.
Biror element tirik bo‘lgan har bir oraliq daraxtning $O(\log n)$ ta tuguniga bo‘linadi.
Tuzilma haqida nimanidir bilmoqchi bo‘lgan har bir so‘rovni mos bargga joylashtiramiz.
Endi barcha so‘rovlarni qayta ishlash uchun segment daraxtida DFS yuritamiz.
Tugunga kirganda shu tugun ichidagi barcha elementlarni qo‘shamiz.
So‘ng shu tugunning farzandlariga o‘tamiz yoki (tugun barg bo‘lsa) so‘rovlarga javob beramiz.
Tugundan chiqayotganda qo‘shishlarni bekor qilishimiz (undo) kerak.
E’tibor bering: agar tuzilmani $O(T(n))$ vaqtda o‘zgartira olsak, o‘zgarishlar stekini saqlab, o‘zgarishlarni ham $O(T(n))$ vaqtda orqaga qaytara (rollback qila) olamiz.
E’tibor bering: rollbacklar amortizatsion murakkablikni buzadi.

## Izohlar {#notes}

Biror narsa tirik bo‘lgan oraliqlar ustida segment daraxti qurish g‘oyasi faqat ma’lumotlar tuzilmalari masalalarida emas, boshqa masalalarda ham qo‘llanishi mumkin.
Quyidagi masalalarga qarang.

## Implementatsiya {#implementation}

Bu implementatsiya [dinamik bog‘langanlik](https://en.wikipedia.org/wiki/Dynamic_connectivity) masalasi uchun.
U qirra qo‘sha oladi, qirrani o‘chira oladi va bog‘langan komponentlar sonini hisoblay oladi.

```cpp
struct dsu_save {
    int v, rnkv, u, rnku;

    dsu_save() {}

    dsu_save(int _v, int _rnkv, int _u, int _rnku)
        : v(_v), rnkv(_rnkv), u(_u), rnku(_rnku) {}
};

struct dsu_with_rollbacks {
    vector<int> p, rnk;
    int comps;
    stack<dsu_save> op;

    dsu_with_rollbacks() {}

    dsu_with_rollbacks(int n) {
        p.resize(n);
        rnk.resize(n);
        for (int i = 0; i < n; i++) {
            p[i] = i;
            rnk[i] = 0;
        }
        comps = n;
    }

    int find_set(int v) {
        return (v == p[v]) ? v : find_set(p[v]);
    }

    bool unite(int v, int u) {
        v = find_set(v);
        u = find_set(u);
        if (v == u)
            return false;
        comps--;
        if (rnk[v] > rnk[u])
            swap(v, u);
        op.push(dsu_save(v, rnk[v], u, rnk[u]));
        p[v] = u;
        if (rnk[u] == rnk[v])
            rnk[u]++;
        return true;
    }

    void rollback() {
        if (op.empty())
            return;
        dsu_save x = op.top();
        op.pop();
        comps++;
        p[x.v] = x.v;
        rnk[x.v] = x.rnkv;
        p[x.u] = x.u;
        rnk[x.u] = x.rnku;
    }
};

struct query {
    int v, u;
    bool united;
    query(int _v, int _u) : v(_v), u(_u) {
    }
};

struct QueryTree {
    vector<vector<query>> t;
    dsu_with_rollbacks dsu;
    int T;

    QueryTree() {}

    QueryTree(int _T, int n) : T(_T) {
        dsu = dsu_with_rollbacks(n);
        t.resize(4 * T + 4);
    }

    void add_to_tree(int v, int l, int r, int ul, int ur, query& q) {
        if (ul > ur)
            return;
        if (l == ul && r == ur) {
            t[v].push_back(q);
            return;
        }
        int mid = (l + r) / 2;
        add_to_tree(2 * v, l, mid, ul, min(ur, mid), q);
        add_to_tree(2 * v + 1, mid + 1, r, max(ul, mid + 1), ur, q);
    }

    void add_query(query q, int l, int r) {
        add_to_tree(1, 0, T - 1, l, r, q);
    }

    void dfs(int v, int l, int r, vector<int>& ans) {
        for (query& q : t[v]) {
            q.united = dsu.unite(q.v, q.u);
        }
        if (l == r)
            ans[l] = dsu.comps;
        else {
            int mid = (l + r) / 2;
            dfs(2 * v, l, mid, ans);
            dfs(2 * v + 1, mid + 1, r, ans);
        }
        for (query q : t[v]) {
            if (q.united)
                dsu.rollback();
        }
    }

    vector<int> solve() {
        vector<int> ans(T);
        dfs(1, 0, T - 1, ans);
        return ans;
    }
};
```

## Masalalar {#problems}

- [Codeforces - Connect and Disconnect](https://codeforces.com/gym/100551/problem/A)
- [Codeforces - Addition on Segments](https://codeforces.com/contest/981/problem/E)
- [Codeforces - Extending Set of Points](https://codeforces.com/contest/1140/problem/F)
