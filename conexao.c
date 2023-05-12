

// cria a conexão com o sensor e retorna um ponteiro NULL em caso de falha
// *chIP: endereço IP do sensor
// *chPort: numero da porta do sensor
void* EthernetScanner_Connect(char *chIP, char *chPort, int iTimeOut)

// verificar o status de conexão
void EthernetScanner_GetConnectStatus(void *pEthernetScanner, int *uiConnectStatus)


// Cria uma conexão UDP com o weCat3D
// *chDestIP: endereço IP do sensor
// *chDestPort: numero da porta do sensor
// *chSrcIP: endereço IP da placa de interface de rede à qual o sensor está conectado
void* EthernetScanner_ConnectUDP(char* chDestIP, char* chDestPort, char* chSrcIP, char* chSrcPort, char* chMode)

// fecha a conexão
void* _stdcall EthernetScanner_Disconnect(void *pEthernetScanner)

