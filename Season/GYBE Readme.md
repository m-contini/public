# [Godspeed You! Black Emperor](https://en.wikipedia.org/wiki/Godspeed_You!_Black_Emperor)

## [Gauss Gun](https://en.wikipedia.org/wiki/Gauss_gun)

![CannoneGauss](<https://static.wikia.nocookie.net/ogame/images/e/ec/Gauss_Cannon.gif/revision/latest?cb=20100501120258&path-prefix=it>)

Il `Cannone Gauss` è un dispositivo che sfrutta l'interazione tra magneti e proiettili per accelerare questi ultimi a velocità molto elevate. Il principio di funzionamento è simile a quello di un'arma elettromagnetica, ma il `Cannone Gauss` non è in grado di sparare proiettili letali.

Assumendo l'assenza di forze non conservative, usiamo il principio di minima azione per cui $\delta S = 0$.

L'azione si può calcolare come segue:

$$
S = \int_{t_1}^{t_2} L \, dt
$$

dove $L$ rappresenta la lagrangiana del sistema. Per un sistema meccanico, la lagrangiana è definita come:

$$
L = T - V
$$

dove $T$ è l'energia cinetica e $V$ è l'energia potenziale. Per un sistema di particelle, l'energia cinetica è data da:

$$
T = \sum_{i=1}^{N} \frac{1}{2} m_i v_i^2
$$

con $m_i$ e $v_i$ rispettivamente la massa e la velocità della particella $i$-esima. L'energia potenziale è data da:

$$
V = \sum_{i=1}^{N} m_i g z_i
$$

con $g$ l'accelerazione di gravità e $z_i$ l'altezza della particella $i$-esima rispetto ad un riferimento.

Per un sistema di particelle, la lagrangiana diventa quindi:

$$
L = \sum_{i=1}^{N} \left( \frac{1}{2} m_i v_i^2 - m_i g z_i \right)
$$

Il principio di minima azione ci permette di ottenere le equazioni del moto per il sistema. In particolare, le equazioni del moto si ottengono imponendo che la variazione della lagrangiana rispetto alle coordinate generalizzate sia nulla:

$$
\frac{d}{dt} \left( \frac{\partial L}{\partial \dot{q}_i} \right) - \frac{\partial L}{\partial q_i} = 0
$$

dove $q_i$ sono le coordinate generalizzate e $\dot{q}_i$ le loro derivate rispetto al tempo. Per il sistema di particelle considerato, le equazioni del moto diventano:

$$
m_i \ddot{z}_i = - m_i g
$$

con $\ddot{z}_i$ la seconda derivata temporale dell'altezza della particella $i$-esima. La soluzione di questa equazione differenziale è:

$$
z_i(t) = z_i(0) - \frac{1}{2} g t^2
$$

con $z_i(0)$ l'altezza iniziale della particella $i$-esima. La velocità della particella $i$-esima è data da:

$$
v_i(t) = - g t
$$

La velocità di una particella dipende quindi solo dal tempo e non dalla posizione. Questo risultato è dovuto al fatto che il `Cannone Gauss` non è in grado di sparare proiettili letali.
