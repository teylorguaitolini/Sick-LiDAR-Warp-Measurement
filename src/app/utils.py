import numpy as np
import matplotlib.pyplot as plt

class Utils:
    def __init__(self) -> None:
        pass

    def _plot(self, scan_list:list[tuple]):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        npoints = 0

        for z, scan in enumerate(scan_list):
            x = scan[0]
            y = scan[1]
            # Plotar os pontos 3D
            ax.scatter(x, y, z, c="g", s=1)

            npoints += len(x)
        
        # Configurações adicionais do gráfico
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Amostras')

        print(f"Leituras: {len(scan_list)}")
        print(f"Total de Pontos: {npoints}")

        # Exibir o gráfico
        plt.show()
    
    def _process(self, scan_list:list[tuple], threshold:float):
        if threshold > 0:
            for i in range(len(scan_list)):
                # Extrair os valores de x e y da leitura atual
                x = np.array(scan_list[i][0])
                y = np.array(scan_list[i][1])

                # --- aplicar um threshold inicial --- #
                idxs = np.where(y > threshold)
                x = np.delete(x, idxs)
                y = np.delete(y, idxs)
                # ---

                # --- aplicar threshold LSC e LIC --- #
                mean = y.mean()
                devi = y.std()
                lcl = mean-2*devi
                ucl = mean+2*devi

                idxs = np.where(y < lcl)
                x = np.delete(x, idxs)
                y = np.delete(y, idxs)

                idxs = np.where(y > ucl)
                x = np.delete(x, idxs)
                y = np.delete(y, idxs)
                # ---

                # substitui a tupla inicial pela reduzida no processamento
                scan_list[i] = (x, y)

        self._plot(scan_list) # plotagem para vizualizar a núvem

        # scan_list é a núvem de pontos para continuar os processamentos