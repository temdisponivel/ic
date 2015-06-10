/* Pino 13 recebe o pulso do echo */
#define echoPin 13

/* Pino 12 envia o pulso para gerar o echo */
#define trigPin 12

void setup()
{
   /* Inicia a porta serial com frequencia de 9600bps */
   Serial.begin(9600);
  
   /* Define o pino 13 como entrada (recebe) */
   pinMode(echoPin, INPUT);
  
   /* Define o pino 12 como saida (envia) */
   pinMode(trigPin, OUTPUT);
}

void loop()
{
    //seta o pino 12 com um pulso baixo "LOW" ou desligado ou ainda 0
    digitalWrite(trigPin, LOW);

    // delay de 2 microssegundos
    delayMicroseconds(2);

    //seta o pino 12 com pulso alto "HIGH" ou ligado ou ainda 1
    digitalWrite(trigPin, HIGH);

    //delay de 10 microssegundos
    delayMicroseconds(10);

    //seta o pino 12 com pulso baixo novamente
    digitalWrite(trigPin, LOW);
    
    /* Pega a duração do echo (ida + volta) com um timeout de 3000 (5 metros) */
    int duracao = pulseIn(echoPin, HIGH, 3000); //pino de saida, 1, timeout do retorno
    
    /* Envia a duração via serial */
    Serial.println(duracao);
    
    /* Espera 1/60 segundos para rodar novamente, o que nos dá 60 medidas por segundo*/
    delay(1000/60);
}
