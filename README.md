# Network Configurator

Network Configurator je orodje za sisteme Windows, ki omogoča enostavno upravljanje z mrežnimi nastavitvami. Program omogoča hitro preklapljanje med različnimi mrežnimi konfiguracijami in shranjevanje pogosto uporabljenih nastavitev.

## Funkcionalnosti

- Upravljanje z mrežnimi karticami
- Nastavitev statičnega IP ali DHCP naslova
- Konfiguracija:
  - IP naslova
  - Subnet maske
  - Gateway naslova
  - DNS strežnikov (primarni in sekundarni)
- Shranjevanje in nalaganje konfiguracij
- Podpora za več mrežnih kartic

## Zahteve

- Windows 10/11 (verjetno tudi server)
- Administratorske pravice

## Namestitev

1. Prenesite najnovejšo verzijo iz [Releases](https://github.com/erikklavora/NetworkConfigurator/releases)
2. Zaženite `NetworkConfigurator.exe`
3. Ob zagonu bo program zahteval administratorske pravice

## Uporaba

1. Izberite mrežno kartico iz spustnega seznama
2. Izberite način (DHCP ali statični IP)
3. V primeru statičnega IP-ja vnesite:
   - IP naslov
   - Subnet masko
   - Gateway
   - DNS strežnike (opcijsko)
4. Kliknite "Nastavi" za aplikacijo nastavitev

### Shranjevanje konfiguracij

1. Nastavite želene parametre
2. Kliknite "Shrani konfiguracijo"
3. Vnesite ime konfiguracije
4. Potrdite shranjevanje

### Nalaganje shranjenih konfiguracij

1. Izberite konfiguracijo iz seznama
2. Kliknite "Naloži izbrano" ali dvokliknite na konfiguracijo

## Tehnične podrobnosti

- Razvito v Python 3
- Uporablja tkinter za GUI
- Shranjuje konfiguracije v JSON formatu
- Uporablja Windows `netsh` ukaze za konfiguracijo

## Varnostne opombe

- Program zahteva administratorske pravice za spreminjanje mrežnih nastavitev
- Konfiguracije so shranjene v uporabniškem profilu
- Ne shranjuje občutljivih podatkov

## Razvoj

Za razvoj potrebujete:
- Python 3.x
- tkinter
- pyinstaller (za kreiranje exe)

##Kloniranje repozitorija:
bash
git clone https://github.com/username/NetworkConfigurator.git

##Kreiranje exe datoteke:
bash
pyinstaller network_config.spec
