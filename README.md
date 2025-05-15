# Projeto-Robotica
Ao iniciar, o robô coloca as posições das caixas em uma lista, as ordenando por proximidade e, assim, começa a visitá-las. Ele gira sobre o mesmo eixo até encontrar o ângulo certo que faça ele andar na direção da primeira caixa da lista, e começa a acelerar. Quando encontra uma caixa, a posição do robô é salva e ele tenta empurrá-la durante 1 segundo. Após esse tempo, a nova posição do robô é comparada com a anterior e caso não haja diferença, o robô não andou e a caixa não é leve. Então, ele tira a respectiva caixa da lista e passa a procurar o ângulo para ir em direção a próxima caixa. Agora, caso haja diferença nas posições registradas, significa que o robô andou, logo a caixa foi empurrada e assim a caixa leve foi encontrada!!











