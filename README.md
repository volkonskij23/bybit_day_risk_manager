# bybit_day_risk_manager
Daily risk manager for the bybit crypto exchange

Дневной риск-менеджер для криптобиржи Bybit.

Для запуска необходимо заполнить конфигурационный файл /json/config.json: <br>

* "tg_token"                  - токен телеграм-бота;
* "user_id"                   - id пользователя бота;
* "api_key"                   - открытый api-ключ, полученный в личном кабинете криптобиржи;
* "api_secret"                - закрытый api-ключ, полученный в личном кабинете криптобиржи;
* "day_stop_loss"             - величина дневного стоп-лосса в процентах;
* "balance_update_time_start" - начало временного периода обновления сведений о балансе кошелька (раз в день обновляется доступный баланс);
* "balance_update_time_end"   - окончание временного периода обновления сведений о балансе кошелька;

При развертывание на VPS рекомендуется создать сервис для управления скриптом: <br>
```console
foo@bar:~$ sudo nano /lib/systemd/system/day_risk_manager.service
```

```
  [Unit]
  Description=Dummy Service
  After=multi-user.target
  Conflicts=getty@tty1.service
  
  [Service]
  WorkingDirectory=path/to/dir/with/script
  Type=simple
  ExecStart=/usr/bin/python3 main.py
  Restart=on-failure
  RestartSec=5
  [Install]
  WantedBy=multi-user.target

```
```console
foo@bar:~$ sudo systemctl daemon-reload
foo@bar:~$ sudo systemctl enable day_risk_manager.service
foo@bar:~$ sudo systemctl start  day_risk_manager.service
```
