import random

class Processador:
    def __init__(self):
        self.processos = []
        self.ready = []
        self.blocked = []
        self.exit = []
        self.running = None
        self.acumulador = 0
        self.PC = 0
        self.contador = 0

    def add_ready(self,processo):
        add = 0
        if len(self.ready) == 0:
            self.ready.insert(0,processo)
        else:
            for index , x in enumerate(self.ready):
                if self.ready[index].prioridade > processo.prioridade:
                    add = index
                elif index == len(self.ready) - 1:
                    add = -1

            if add == -1:
                self.ready.append(processo)
            else:
                self.ready.insert(index,processo)


    def add_exit(self,processo):
        self.exit.append(processo)
        self.processos.remove(processo)
        
    def processos_existentes (self):
        return len(self.processos)

    def check_prioridade(self):

        if self.running == None:
            self.running = self.ready.pop(0)
            self.troca_contexto(self.running)
        else:
            if self.running.prioridade > self.ready[0].prioridade:
                aux = self.running
                self.salva_contexto(aux)
                aux.estado = "Ready"
                self.running = self.ready.pop(0)
                self.troca_contexto(self.running)
                self.add_ready(aux)
                self.running.estado = "Running"
                

    def add_run(self,processo):
        self.running = processo
        self.troca_contexto(processo)
        self.ready.remove(processo)
        self.running.estado = "Running"
        self.contador = self.running.quantum

    def salva_contexto(self,processo):
        processo.PC = self.PC
        processo.acumulador = self.acumulador
    

    def troca_contexto(self,processo):
        self.PC = processo.PC
        self.acumulador = processo.acumulador

    def comando(self):

        comando = self.running.instrucoes[self.PC]
        self.PC +=1

        print(comando)
        if comando[0] == "add":
            if comando[1][0] == "#":
                op = comando[1][1:]
            else:
                op = self.running.variaveis[comando[1]]

            self.add(int(op))

        if comando[0] == "sub":
            if comando[1][0] == "#":
                op = comando[1][1:]
            else:
                op = self.running.variaveis[comando[1]]

            self.sub(int(op))

        if comando[0] == "div":
            if comando[1][0] == "#":
                op = comando[1][1:]
            else:
                op = self.running.variaveis[comando[1]]

            self.div(int(op))

        if comando[0] == "mult":
            if comando[1][0] == "#":
                op = comando[1][1:]
            else:
                op = self.running.variaveis[comando[1]]

            self.mult(int(op))

        elif comando[0] == "load":
            self.acumulador = int(self.running.variaveis[comando[1]])
        elif comando[0] == "store":
            self.running.variaveis[comando[1]] = self.acumulador
        elif comando[0] == "BRANY":
            print("pc ",self.running.labels[comando[1]])
            self.PC = self.running.labels[comando[1]]

        elif comando[0] == "BRZERO":
            if self.acumulador == 0:
                self.PC = self.running.labels[comando[1]]

        elif comando[0] == "BRPOS":
            if self.acumulador > 0:
                self.PC = self.running.labels[comando[1]]

        elif comando[0] == "BRNEG":
            if self.acumulador < 0:
                self.PC = self.running.variaveis[comando[1]]

        elif comando[0] == "syscall":
            if comando[1] == "0":
                
                self.exit = self.running
                self.processos.remove(self.running)
                self.running = None

            elif comando[1] == "1":
                print("PRINT DO PROGRAMA: ", self.acumulador)
                self.running.bloqueado = random.randint(10,20)
                self.blocked.append(self.running)
                self.salva_contexto(self.running)
                self.contador = 0
                self.running = None
            elif comando[1] == "2":
                x = int(input("Digite o numero: "))
                self.acumulador = x
                self.running.bloqueado = random.randint(10,20)
                self.blocked.append(self.running)
                self.salva_contexto(self.running)
                self.contador = 0
                self.running = None

                

    def add(self,op):
        self.acumulador = self.acumulador + int(op)
    
    def sub(self,op):
        self.acumulador = self.acumulador - op

    def mult(self,op):
        self.acumulador = self.acumulador * op

    def div(self,op):
        self.acumulador = self.acumulador/op


    def check_empty(self):
        if len(self.ready) == 0 and len(self.blocked) == 0 and self.running == None:
            return True

        return False

    def check_timing(self):
        for x in self.blocked:
            x.bloqueado -= 1
            if x.bloqueado == 0:
                self.add_ready(x)
                self.blocked.remove(x)

class PCB:
    def __init__ (self,codigo):
        self.ref = 0
        self.prioridade = 2
        self.codigo = codigo
        self.labels = {}
        self.variaveis = self.set_data(codigo)
        self.instrucoes = self.set_instrucoes(codigo)
        self.bloqueado = 0
        self.PC = 0
        self.acumulador = 0
        self.estado = "Ready"
        self.quantum = 0

    def set_instrucoes(self,codigo):
        inst = []
        qtdade_labels = 0
        for index, x in enumerate(codigo[1:]):   
            if x == ".endcode":
                return inst
            elif x[len(x)-1] == ":":
                self.labels[x[:len(x)-1]] = index - qtdade_labels
                qtdade_labels += 1
            else:
                z = x.split(" ")
                inst.append((z[0],z[1]))


    def set_data(self,codigo):
        memoria = {}
        data = 0
        for i in range (0,len(codigo)):
            if codigo[i] == '.data':
                data = i+1

        for i in range (data,len(codigo)-1):
            variavel = codigo[i].split(' ')
            memoria[variavel[0]] = variavel[1]

        return memoria

def leitura (arquivo):
    
    codigo = []
    arq = open(arquivo)
    linhas = arq.readlines()
    count = 0

    for line in linhas:
        if line != '\n':
            codigo.append(line.strip())

    arq.close()
    return codigo

def executar(SO):
    while not SO.check_empty():
        for x in SO.ready:
            print(x.ref, "pronto")
        for x in SO.blocked:
            print(x.ref,"bloqueado por",x.bloqueado, "unidades de tempo")
        if len(SO.ready) > 0:
            SO.check_prioridade()
        if SO.running != None:
            print(SO.running.ref, "rodando")
            SO.comando()
        else:
            print("Nenhum programa no processador")
        SO.check_timing()

def executar_RR(SO):
    while not SO.check_empty():
        for x in SO.ready:
            print(x.ref,"pronto")
        for x in SO.blocked:
            print(x.ref,"bloqueado por",x.bloqueado, "unidades de tempo")
        if SO.running != None:
            print(SO.running.ref, "rodando")
        if SO.contador == 0 and len(SO.ready)>0:
            SO.add_run(SO.ready[0])
            SO.contador -= 1
            SO.comando()
            if SO.contador == 0 and SO.running != None:
                SO.salva_contexto(SO.running)
                SO.ready.append(SO.running)
                SO.running.estado = "Ready"
                SO.running = None

        elif SO.running != None:
            SO.contador -= 1
            SO.comando()
            if SO.contador == 0 and SO.running != None:
                SO.salva_contexto(SO.running)
                SO.ready.append(SO.running)
                SO.running.estado = "Ready"
                SO.running = None
        
        SO.check_timing()
        
        


        

arquivos = []
codigo = []
SO = Processador()

algoritmo = str(input("Qual tipo de politica deve ser aplicada? Round Robin 'R' ou prioridade 'P': "))
if algoritmo == 'P' or algoritmo == 'p':
    x = str(input("Digite o nome do primeiro arquivo: "))
    z = str(input("Qual a prioridade do processo? "))
    arquivos.append((x,z))
    while (1):
        y = str(input("Voce deseja adicionar outro arquivo? S/N "))
        if y == 'N':
            break
        elif y == "S":
            x = str(input("Digite o nome do arquivo: "))
            z = str(input("Qual a prioridade do processo? "))
            arquivos.append((x,z))
        else:
            print("Resposta invalida")

    

    for x in arquivos:
        codigo.append((leitura(x[0]),x[1]))

    proc = []
    for index, x in enumerate(codigo):  
        proc.append(PCB(x[0]))
        proc[index].ref = len(proc)
        proc[index].prioridade = x[1]


    for x in proc:
        SO.processos.append(x)
        SO.add_ready(x)

    executar(SO)

elif algoritmo == 'R' or algoritmo == 'r':
    x = str(input("Digite o nome do primeiro arquivo: "))
    z = str(input("Quantas unidades de tempo o processo deve executar? "))
    arquivos.append((x,z))
    while (1):
        y = str(input("Voce deseja adicionar outro arquivo? S/N "))
        if y == 'N' or y == 'n':
            break
        elif y == "S" or y == 's':
            x = str(input("Digite o nome do arquivo: "))
            z = str(input("Quantas unidades de tempo o processo deve executar? "))
            arquivos.append((x,z))
        else:
            print("Resposta invalida")

    

    for x in arquivos:
        codigo.append((leitura(x[0]),x[1]))

    proc = []
    for index, x in enumerate(codigo):  
        proc.append(PCB(x[0]))
        proc[index].ref = len(proc)
        proc[index].quantum = int(x[1])

    for x in proc:
        SO.processos.append(x)
        SO.ready.append(x)

    executar_RR(SO)
else:
    print("Entrada invalida")
    exit()