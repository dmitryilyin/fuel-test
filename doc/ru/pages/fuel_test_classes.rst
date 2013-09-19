============================================
Appendix B -- Структура директорий Fuel-test
============================================

Набор тестов для Fuel и инфраструктура 
---------------------------------------

Тесты сводятся к созданию виртуального окружения и развертывания в нем OpenStack при помощи Fuel. 
Также эти тесты используются для подготовки окружения для прогона  набора тестов Tempest [1]_.

директории fuel_test  ( в том же репозитории, что и Fuel: https://github.com/Mirantis/fuel.git	 ):
 * ci		классы реализующие окружения для CI-тестов
 * config	конфигурационные файлы для tempest* test suite
 * doc		документация 
 * helpers	вспомогательные модули и функции
 * puppet_tests	скрипты для интеграционного тестирования модулей puppet
 * tempest	скрипты для подготовки и прогона набора тестов Tempest
 * tests	тесты для разных вариантов развертывания OpenStack


остальные файлы:
 * settings.py	общие настройки для всех тестов развертывания OpenStack
 * prepare.py	конфигурационные файлы для tempest* test suite
 * pip-requires	список зависимостей для тестов

.. [1]  Tempest --- это набор интеграционных тестов для Openstack (  https://github.com/openstack/tempest )


Библиотека devops
-----------------

Библиотека позволяет создавать виртульные окружения через libvirt для тестирования.

Структура директорий:
 * devops ( в отдельном репозитории https://github.com/Mirantis/devops.git  )
 * bin	dos.py --- оболочка для управления виртуальными окружениями
 * devops	файлы библиотеки Devops
 * docs	заготовки для документации (пустые), getstart.rst (как начать работу)
 * samples	примеры как создавать виртуальные окружения при помощи devops


Классы и методы
----------------



Классы для создания виртуальных окружений ( fuel_test/ci )  
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*CiBase* ( ci_base.py )  --- базовый класс для подготовки тестового окружения (группа VM) для интеграционного тестирования (CI)

*CiVM* ( ci_bm.py  ) ---  класс для развертывания тестового окружения на виртуальных машинах (VM)

*CiBM* ( ci_vm.py ) ---  класс для развертывания тестового окружения на физических машинах (BM=Bare Metal)

Эти классы используются в нижеописанных FullTestCase, CompactTestCase, SimpleTestCase, SingleTestCase и прочих тестах на развертывание OpenStack в соответствующих вариантах ( deployment mode ).





Классы для запуска тестовых сценариев ( fuel_test/tests )
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

(С) FullTestCase - класс для развертывания тестового окружения для интеграционного тестирования (CI). Данный класс реализует метод-тест test_full который предполагается запускать через nosetests ( https://nose.readthedocs.org ). Метод выполняет развертывание OpenStack в варианте “Multi node HA Standalone” посредством Fuel. Фактически тут один тест, который ничего кроме деплоймета OpenStack не выполняет. Также реализованы и все остальные классы CompactTestCase, MinimalTestCase, SimpleTestCase,  SingleTestCase для других вариантов развертывания.

Методы класса  FullTestCase :
 *  deploy	запускает развертывание одним из выбранных способом (через astute или без )
 *  deploy_one_by_one	развертывание через манифесты puppet
 *  deploy_by_astute	развертывание через astute
 *  prepare_astute	создает конфигурационные файлы для astute и настраивает cobbler
 *  test_full 	запускает тест на развертывание используя метод deploy, делает снимки состояния виртуальных машин



(С) CompactTestCase  (  test_compact.py ) -  класс реализует раличные варианты развертывания OpenStack в варианте Multi-node (HA) deployment (Compact) посредством Fuel.

Методы класса  CompactTestCase:
 * deploy_compact	запускает развертывание на нодах через puppet agent, метод используется во всех методах-тестах 
 * test_deploy_compact_quantum    тест на развертывание с Quantum на контроллерах
 * test_deploy_compact_quantum_standalone тест на развертывание с Quantum на отдельной ноде
 * test_deploy_compact_wo_quantum --- тест на  развертывание без Quantum 
 * test_deploy_compact_wo_quantum_cinder_all_by_ipaddr --- тест на  развертывание с Cinder на всех нодах, но без Quantum, Cinder-ные ноды задаются списком ip-адресов нод
 * test_deploy_compact_wo_quantum_cinder_all --- тест на  развертывание с Cinder на всех нодах, но без Quantum, Cinder-ные ноды задаются через cinder_nodes=['all']
 * test_deploy_compact_wo_loopback --- --- тест на  развертывание с Cinder на контроллерах, с параметром SWIFT loopback
 * test_deploy_compact_wo_ha_provider ---  на  развертывание с Cinder на контроллерах, без HA
 * deploy_by_astute	развертывание через astute ( КМК метод дублируется в нескольких классах и напрашивается на рефакторинг )


(С) MinimalTestCase (  test_minimal.py ) ---  класс реализует развертывание OpenStack в варианте Multi-node (HA) deployment (Compact) посредством Fuel.

Методы класса  MinimalTestCase:
 * deploy --- запускает развертывание выбранным способом (через astute или без )
 * deploy_one_by_one 	развертывание через манифесты puppet
 * deploy_by_astute 	развертывание через astute
 * prepare_astute 	создает конфигурационные файлы для astute и настраивает cobbler
 * test_minimal  ---  запускает тест на развертывание используя метод deploy, делает снимки состояния виртуальных машин


(С) SimpleTestCase  (  test_minimal.py )

Методы класса MinimalTestCase:
 * deploy 
 * deploy_one_by_one 
 * deploy_by_astute 
 * prepare_only_site_pp 
 * prepare_astute 
 * test_simple 



(С) NoopTestCase	прогон всех модулей puppet из /etc/puppet/modules с опцией --noop

Методы класса    NoopTestCase:
 * test_apply_all_modules_with_noop --- прогон всех модулей puppet из /etc/puppet/modules с опцией --noop ( т.е. тест всех  модулей puppet типа  syntax check / dependencies check / etc. без фактического внесения изменений в систему )

---

(С) NovaSubClassesTestCase ( test_nova_subclasses.py ) ---

Методы класса    NovaSubClassesTestCase:
 * setUp 
 * test_deploy_nova_compute 
 * test_deploy_nova_api_compute 
 * test_deploy_nova_api_controller 
 * test_deploy_nova_network 
 * test_deploy_nova_consoleauth 
 * test_deploy_nova_rabbitmq 
 * test_deploy_nova_utilities 
 * test_deploy_nova_vncproxy 
 * test_deploy_nova_volume 


---




(С) CobblerClient ( cobbler_client.py ) 
    взаимодействие с Cobbler через его  XML RPC 
 
---

(С) CobblerTestCase ( vm_test_case.py )
    базовый класс на основе которого реализуются классы для тест-кейсов по развертыванию в разных вариантах ( “Single node”, “Multi node HA Standalone”,  “Multi node HA Compact SWIFT”, и т.д. )
 
---

(C) CobblerTestCase ( test_cobbler.py )
     ненужный тест класс-пустышка (  Настя уже удалила из репозитория )
 
---

(C) BaseTestCase ( base_test_case.py )
    базовый родительский класс производный от TestCase из модуля TestCase на основе которого построен  CobblerTestCase ( vm_test_case.py )  и далее по иерархии  все остальные классы-тесты.
 
---

Вспомогательные модули, классы и их методы
Классы:

(С) Astute ( astute.py)
    (F) config
    (F) test_minimal_config 
    (F) __init__	


(С) Config ( config.py ) --- 
    (F) generate
    (F) yaml.safe_dump
    (F) orchestrator_common
    (F) openstack_common
    (F) ci.public_router
    (F) cobbler_common
    (F) get_ks_meta
    (F) cobbler_nodes



(С) SelfTest ( iso_master.py ) --- 
    (F) get_config
    (F) _get_config
    (F) test_config 


(С) Manifest ( manifest.py ) --- 


(С) Template ( manifest.py ) ---
 
(С) Nodes ( node_roles.py  ) --- 

(С) NodeRoles ( node_roles.py  ) --- 

(С) Prepare  ( prepare.py ) --- 

(С) TestConfig  ( test_config.py ) --- 

(С) TestManifest  ( test_manifest.py ) --- 










Модуль  helpers.py ( переименован в functions.py)
   содержит вспомогательные функции:
     *  get_file_as_string --- считывает файл и выдает его содержимое ( удалено )
     *  udp_ping --- проверяет доступность заденного UDP порта
     *  tcp_ping --- проверяет доступность заденного TCP порта
     *  load  ---  считывает файл и выдает его содержимое
     *  extract_virtual_ips ---  извлекает IP-адреса из строки в dict
     *  write_config  ---  записывает конфиг. файл на заданный удаленный хост
     *  retry  ---  повторяет выполнение заданной функции до тех пор пока она не выполнится или истечет число возможных попыток. Между выполнениями делает 1 сек пауза.
     *  install_packages2  ---  устанавливает на заданных хостах пакеты
     *  install_packages  ---  устанавливает на заданном хосте пакеты
     *  update_pms  ---  обновляет метаданные репозиториев на заданных хостах
     *  update_pm  ---  обновляет метаданные репозиториев на заданном хосте
     *  add_nmap  ---  устанавливает пакет nmap на заданном хосте
     *  add_epel_repo_yum  ---  добавляет репозиторий EPEL на хост ( через установку пакета epel-release-6-8.noarch.rpm )
     *  delete_epel_repo_yum  ---   удаляет репозиторий EPEL с заданного хоста 
     *  add_puppet_lab_repo  ---  добавляет репозиторий puppetlabs на хост ( через установку пакета )
     *  remove_puppetlab_repo ---  удаляет репозиторий puppetlabs с хоста
     *  setup_puppet_client  ---  запускает  puppet на заданном хосте
     *  start_puppet_master  ---   запускает  puppet на заданном хосте
     *  start_puppet_agent  ---  запускает  puppet на заданном хосте
     *  request_cerificate  ---  проверяет наличие сертификата на хосте
     *  switch_off_ip_tables  ---  удаляет все правила на хосте ( через iptables -F )
     *  puppet_apply  --- выполняет  puppet apply на  заданном хосте 
     *  setup_puppet_master  ---  настраивает и запускает puppet на заданном хосте 
     *  upload_recipes  ---  загружает модули puppet  в /etc/puppet/modules/ ( через recipes.tar )
     *  upload_keys  ---  загружает ssh-ключи на заданный хост 
     *  change_host_name  ---  задает имя удаленного хоста
     * update_host_name_centos  ---  задает имя удаленного хоста через /etc/sysconfig/network
     * update_host_name_ubuntu  ---  задает имя удаленного хоста через /etc/hostname
     * add_to_hosts  ---  добавляет строчку в /etc/hosts на удаленном хосте
     * check_node_ready  ---  проверяет через cobbler готовность ноды
     * await_node_deploy  ---  проверяет через cobbler доступность ноды
     * build_astute  ---  собирает astute.gem на хосте используя gem и gemspec
     * install_astute  ---  устанавливает astute через gem
     * is_not_essex  ---  проверяет версию OpenStack используя переменные окружения


---



Класс PrepareTempest 
--------------------


Класс PrepareTempestCI
----------------------



