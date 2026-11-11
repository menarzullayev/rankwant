# Determinantni Kraut usuli bilan $O(N^3)$ vaqtda hisoblash {#calculating-the-determinant-using-kraut-method-in-on3}

Ushbu maqolada Kraut usuli yordamida matritsa determinantini $O(N^3)$ vaqtda topish bayon qilinadi.

Kraut algoritmi $A$ matritsaning $A = L U$ yoyilmasini topadi, bunda $L$ — quyi uchburchak, $U$ esa yuqori uchburchak matritsa. Umumiylikni yo‘qotmasdan $L$ ning barcha diagonal elementlarini 1 ga teng deb hisoblash mumkin. Bu matritsalarni bilganimizdan keyin $A$ ning determinantini hisoblash oson: u $U$ matritsaning bosh diagonalidagi barcha elementlar ko‘paytmasiga teng.

Har qanday teskarilanuvchi matritsa LU-yoyilmaga ega ekanini, bu yoyilma esa faqat va faqat barcha bosh minorlari noldan farqli bo‘lgandagina yagona bo‘lishini tasdiqlovchi teorema mavjud. Biz faqat $L$ matritsaning diagonali birlardan iborat bo‘lgan yoyilmani qaraymiz.

$A$ matritsa, $N$ esa uning o‘lchami bo‘lsin. $L$ va $U$ matritsalarning elementlarini quyidagi qadamlar bilan topamiz:

 1. $i = 1, 2, ..., N$ uchun $L_{i i} = 1$ deb olamiz.
 2. Har bir $j = 1, 2, ..., N$ uchun quyidagilarni bajaramiz:
    - $i = 1, 2, ..., j$ uchun qiymatlarni topamiz

      $$
      U_{ij} = A_{ij} - \sum_{k=1}^{i-1} L_{ik} \cdot U_{kj}
      $$

    - So‘ng $i = j+1, j+2, ..., N$ uchun qiymatlarni topamiz

      $$
      L_{ij} = \frac{1}{U_{jj}} \left(A_{ij} - \sum_{k=1}^{j-1} L_{ik} \cdot U_{kj} \right).
      $$

## Implementatsiya {#implementation}

```java
static BigInteger det (BigDecimal a [][], int n) {
	try {

	for (int i=0; i<n; i++) {
		boolean nonzero = false;
		for (int j=0; j<n; j++)
			if (a[i][j].compareTo (new BigDecimal (BigInteger.ZERO)) > 0)
				nonzero = true;
		if (!nonzero)
			return BigInteger.ZERO;
	}

	BigDecimal scaling [] = new BigDecimal [n];
	for (int i=0; i<n; i++) {
		BigDecimal big = new BigDecimal (BigInteger.ZERO);
		for (int j=0; j<n; j++)
			if (a[i][j].abs().compareTo (big) > 0)
				big = a[i][j].abs();
		scaling[i] = (new BigDecimal (BigInteger.ONE)) .divide
			(big, 100, BigDecimal.ROUND_HALF_EVEN);
	}

	int sign = 1;

	for (int j=0; j<n; j++) {
		for (int i=0; i<j; i++) {
			BigDecimal sum = a[i][j];
			for (int k=0; k<i; k++)
				sum = sum.subtract (a[i][k].multiply (a[k][j]));
			a[i][j] = sum;
		}

		BigDecimal big = new BigDecimal (BigInteger.ZERO);
		int imax = -1;
		for (int i=j; i<n; i++) {
			BigDecimal sum = a[i][j];
			for (int k=0; k<j; k++)
				sum = sum.subtract (a[i][k].multiply (a[k][j]));
			a[i][j] = sum;
			BigDecimal cur = sum.abs();
			cur = cur.multiply (scaling[i]);
			if (cur.compareTo (big) >= 0) {
				big = cur;
				imax = i;
			}
		}

		if (j != imax) {
			for (int k=0; k<n; k++) {
				BigDecimal t = a[j][k];
				a[j][k] = a[imax][k];
				a[imax][k] = t;
			}

			BigDecimal t = scaling[imax];
			scaling[imax] = scaling[j];
			scaling[j] = t;

			sign = -sign;
		}

		if (j != n-1)
			for (int i=j+1; i<n; i++)
				a[i][j] = a[i][j].divide
					(a[j][j], 100, BigDecimal.ROUND_HALF_EVEN);

	}

	BigDecimal result = new BigDecimal (1);
	if (sign == -1)
		result = result.negate();
	for (int i=0; i<n; i++)
		result = result.multiply (a[i][i]);

	return result.divide
		(BigDecimal.valueOf(1), 0, BigDecimal.ROUND_HALF_EVEN).toBigInteger();
	}
	catch (Exception e) {
		return BigInteger.ZERO;
	}
}
```
