from controller import Supervisor
import math

TIME_STEP = 32
QtddSensoresProx = 8
QtddLeds = 10

def ordenar_caixas_por_proximidade(pos_caixas, pos_robo):
    menor_dist = float('inf')
    indice_mais_proxima = 0
    for i, pos in enumerate(pos_caixas):
        dx = pos[0] - pos_robo[0]
        dz = pos[1] - pos_robo[1]
        dist = math.sqrt(dx ** 2 + dz ** 2)
        if dist < menor_dist:
            menor_dist = dist
            indice_mais_proxima = i

    if indice_mais_proxima != 0:
        pos_caixas[0], pos_caixas[indice_mais_proxima] = pos_caixas[indice_mais_proxima], pos_caixas[0]

# Inicializa supervisor
robot = Supervisor()

# Motores
motor_esq = robot.getDevice("left wheel motor")
motor_dir = robot.getDevice("right wheel motor")
motor_esq.setPosition(float('inf'))
motor_dir.setPosition(float('inf'))
motor_esq.setVelocity(0)
motor_dir.setVelocity(0)

# Sensores de proximidade
sensor_prox = []
for i in range(QtddSensoresProx):
    sensor = robot.getDevice(f"ps{i}")
    sensor.enable(TIME_STEP)
    sensor_prox.append(sensor)

# LED
led0 = robot.getDevice("led0")
led0.set(-1)

numero_de_caixas = 10 #indica o numero de caixas !!!PRECISA SER MODIFICADO DE ACORDO COM A QUANTIDADE DE CAIXAS!!!!!!!!!!!!!!
pos_caixas = [] #mostra as posicoes das caixas
caixas_dict = {} #dicionario que contem o nome das caixas

for i in range(1, numero_de_caixas + 1):
    nome = f"CAIXA{i}" #!!!! AS CAIXAS PRECISAM SEGUIR O PADRAO DE NOMES (CAIXAn)
    caixa = robot.getFromDef(nome) #identifica a caixa
    if caixa is not None: # se ela existir
        caixas_dict[nome] = caixa  # salva como CAIXA1, CAIXA2 por diante, para futuramente usar para pegar a posicao em tempo real
        pos = caixa.getPosition() #Pega a posicao de quando o mundo e gerado 
        pos_caixas.append(pos) #adiciona a posicao original das caixas na lista de posicoes
    else:
        print(f"Erro: {nome} não encontrada")


# identifica as caixas ALTERAR DE ACORDO COM A QUANTIDADE DE CAIXAS
# caixa1 = robot.getFromDef("CAIXA1")
# caixa2 = robot.getFromDef("CAIXA2")
# caixa3 = robot.getFromDef("CAIXA3")
# caixa4 = robot.getFromDef("CAIXA4")

# # adiciona as posicoes das caixas em uma lista
# pos_caixas = [
#     caixa1.getPosition(), #[x,y,z]
#     caixa2.getPosition(),
#     caixa3.getPosition(),
#     caixa4.getPosition()
# ]

empurrando_caixa = False
caixa_leve_encontrada = False

# Loop principal
while robot.step(TIME_STEP) != -1:
    if(len(pos_caixas)>0):
        #posicao do robo
        pos_robo = robot.getSelf().getPosition()
        #rotacao do robo
        rot_robo = robot.getSelf().getOrientation()

        # ordena a lista de caixas, mantendo a que possui a posicao mais perto no indice 0
        ordenar_caixas_por_proximidade(pos_caixas, pos_robo)

        # Leitura dos sensores de proximidade
        leitura_sensor_prox = []
        for i, sensor in enumerate(sensor_prox):
            valor = sensor.getValue() - 60
            leitura_sensor_prox.append(valor)


        dx = pos_caixas[0][0] - pos_robo[0] #acessa o primeiro elemento da lista de posicoes, pegando a posicao x
        dy = pos_caixas[0][1] - pos_robo[1] #acessa o primeiro elemento da lista de posicoes, pegando a posicao y
        angulo_desejado = math.atan2(dy, dx) #calcula o angulo que o robo precisa virar para seguir em direcao da caixa
        angulo_robo = math.atan2(rot_robo[1], rot_robo[0]) #calula o angulo atual do robo
        erro_angular = angulo_desejado + angulo_robo #calcula o erro angular, para indicar quando deve seguir em frente
        distancia = math.sqrt(dx**2 + dy**2) #calcula a distancia do robo para a caixa alvo 

        #imprime as informacoes para depuracao
        print(f"Angulo desejado: {angulo_desejado:.4f} | Angulo do robo: {angulo_robo:.4f} | Erro angular: {erro_angular:.4f} | Distancia: {distancia:.4f} | Posicao Caixa (X,Y): {pos_caixas[0][0]:.4f}, {pos_caixas[0][1]:.4f}")

        if(distancia>0.09):
            # Controle de movimento
            if (-0.15 < erro_angular <= 0.15): #se o erro angular for baixo, o robo segue em linha reta
                velocidade = 4.0
                acelerador_esq = 1.0
                acelerador_dir = 1.0
            else: #caso contrario, comeca a girar ate achar o angulo correto
                velocidade = 2.0
                acelerador_esq = 1.0
                acelerador_dir = -1.0
        else:
            teste = True
            while teste:
                robot.step(TIME_STEP)
                tempo_total = 1000  # milissegundos

                if not empurrando_caixa:
                    print("Caixa encontrada. Iniciando empurrão...")
                    empurrando_caixa = True
                    tempo_empurrando = 0
                    pos_ini = robot.getSelf().getPosition()
                    velocidade = 4.0
                    acelerador_esq = 1.0
                    acelerador_dir = 1.0
                else:
                    tempo_empurrando += TIME_STEP
                    if tempo_empurrando >= tempo_total:
                        pos_fin = robot.getSelf().getPosition()
                        dx = pos_ini[0] - pos_fin[0]
                        dy = pos_ini[1] - pos_fin[1]
                        dist = math.sqrt(dx**2 + dy**2)
                        if dist > 0.06:
                            caixa_leve_encontrada = True
                            break
                        else:
                            print("Caixa pesada. Indo para a próxima.")
                            pos_caixas.pop(0)
                            empurrando_caixa = False
                            teste = False
            if caixa_leve_encontrada:
                print("Caixa Leve Encontrada!")
                piscar_estado = False
                tempo = 0
                duracao = 4000  # 3 segundos

                while robot.step(TIME_STEP) != -1 and tempo < duracao:
                    # Alterna o LED a cada 200ms
                    if tempo % 200 == 0:
                        piscar_estado = not piscar_estado
                        led0.set(1 if piscar_estado else 0)

                    # Gira parado
                    motor_esq.setVelocity(3.0)
                    motor_dir.setVelocity(-3.0)

                    tempo += TIME_STEP

                # Para o robô e apaga o LED
                motor_esq.setVelocity(0)
                motor_dir.setVelocity(0)
                led0.set(0)
                break

    else:
        print("Nao ha caixa leve")
        acelerador_esq = 0
        acelerador_dir = 0
        break
    
    
    #acelera o robo
    motor_esq.setVelocity(velocidade * acelerador_esq)
    motor_dir.setVelocity(velocidade * acelerador_dir)
