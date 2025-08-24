## Reliable Product Launches at Scale
## 可靠的大規模產品發布

Written by Rhandeev Singh and Sebastian Kirsch with Vivek Rau Edited by Betsy Beyer
作者：Rhandeev Singh 和 Sebastian Kirsch 與 Vivek Rau，編輯：Betsy Beyer

Internet companies like Google are able to launch new products and features in far more rapid iterations than traditional companies. Site Reliability’s role in this process is to enable a rapid pace of change without compromising stability of the site. We created a dedicated team of “Launch Coordination Engineers” to consult with engineering teams on the technical aspects of a successful launch.
像 Google 這樣的網路公司，能夠以比傳統公司快得多的速度推出新產品和功能。網站可靠性 (Site Reliability) 在此過程中的作用是，在不損害網站穩定性的前提下，實現快速的變革。我們成立了一個由「發布協調工程師 (Launch Coordination Engineers)」組成的專門團隊，就成功發布的技術方面向工程團隊提供諮詢。

The team also curated a “launch checklist” of common questions to ask about a launch, and recipes to solve common issues. The checklist proved to be a useful tool for ensuring reproducibly reliable launches.
該團隊還整理了一份「發布檢查清單」，其中包含有關發布的常見問題，以及解決常見問題的方法。事實證明，該檢查清單是確保可重複的可靠發布的有用工具。

Consider an ordinary Google service for example, Keyhole, which serves satellite imagery for Google Maps and Google Earth. On a normal day, Keyhole serves up to several thousand satellite images per second. But on Christmas Eve in 2011, it received 25 times its normal peak traffic upward of one million requests per second. What caused this massive surge in traffic?
以一個普通的 Google 服務為例，Keyhole，它為 Google 地圖和 Google 地球提供衛星影像。在正常的一天，Keyhole 每秒提供多達數千張衛星影像。但在 2011 年的平安夜，它收到的流量是正常高峰期的 25 倍，每秒高達一百萬次請求。是什麼導致了這次巨大的流量激增？

## Santa was coming.
## 聖誕老人來了。

A few years ago, Google collaborated with NORAD (the North American Aerospace Defense Command) to host a Christmas-themed website that tracked Santa’s progress around the world, allowing users to watch him deliver presents in real time. Part of the experience was a "virtual fly-over," which used satellite imagery to track Santa’s progress over a simulated world.
幾年前，Google 與北美航太防衛司令部 (NORAD) 合作，架設了一個以聖誕節為主題的網站，追蹤聖誕老人在世界各地的行蹤，讓使用者可以即時觀看他派送禮物。體驗的一部分是「虛擬飛越」，它使用衛星影像在一個模擬的世界中追蹤聖誕老人的進度。

While a project like NORAD Tracks Santa may seem whimsical, it had all the characteristics that define a difficult and risky launch: a hard deadline (Google couldn’t ask Santa to come a week later if the site wasn’t ready), a lot of publicity, an audience of millions, and a very steep traffic ramp-up (everybody was going to be watching the site on Christmas Eve). Never underestimate the power of millions of kids anxious for presents this project had a very real possibility of bringing Google’s servers to their knees.
雖然像「NORAD 追蹤聖誕老人」這樣的專案看起來可能異想天開，但它具備了所有定義一個困難且有風險的發布的特徵：一個硬性的截止日期（如果網站沒準備好，Google 不能要求聖誕老人晚一週再來）、大量的宣傳、數百萬的觀眾，以及一個非常陡峭的流量爬升（每個人都會在平安夜觀看這個網站）。永遠不要低估數百萬焦急等待禮物的孩子的力量——這個專案很有可能讓 Google 的伺服器不堪重負。

Google’s Site Reliability Engineering team worked hard to prepare our infrastructure for this launch, making sure that Santa could deliver all his presents on time under the watchful eyes of an expectant audience. The last thing we wanted was to make children cry because they couldn’t watch Santa deliver presents. In fact, we dubbed the various kill switches built into the experience to protect our services "Make-children-cry switches." Anticipating the many different ways this launch could go wrong and coordinating between the different engineering groups involved in the launch fell to a special team within Site Reliability Engineering: the Launch Coordination Engineers (LCE).
Google 的網站可靠性工程 (Site Reliability Engineering) 團隊努力為這次發布準備我們的基礎設施，確保聖誕老人能在期待的觀眾注視下，準時送達所有禮物。我們最不希望的就是讓孩子們因為看不到聖誕老人送禮物而哭泣。事實上，我們將為了保護我們的服務而內建在體驗中的各種緊急關閉開關戲稱為「讓孩子哭開關」。預測這次發布可能出錯的各種方式，並協調參與發布的不同工程團隊，這項任務落在了網站可靠性工程內部的一個特殊團隊身上：發布協調工程師 (Launch Coordination Engineers, LCE)。

Launching a new product or feature is the moment of truth for every company the point at which months or years of effort are presented to the world. Traditional companies launch new products at a fairly low rate. The launch cycle at Internet companies is markedly different. Launches and rapid iterations are far easier because new features can be rolled out on the server side, rather than requiring software rollout on individual customer workstations.
推出新產品或功能對每家公司來說都是關鍵時刻——是將數月或數年的努力成果呈現給世界的時刻。傳統公司推出新產品的頻率相當低。網路公司的發布週期則截然不同。發布和快速迭代要容易得多，因為新功能可以在伺服器端推出，而不需要在個別客戶的工作站上進行軟體部署。

Google defines a launch as any new code that introduces an externally visible change to an application. Depending on a launch’s characteristics the combination of attributes, the timing, the number of steps involved, and the complexity the launch process can vary greatly. According to this definition, Google sometimes performs up to 70 launches per week.
Google 將「發布 (launch)」定義為任何引入對應用程式外部可見變更的新程式碼。根據發布的特性——屬性的組合、時間點、涉及的步驟數量以及複雜性——發布過程可能會有很大的不同。根據這個定義，Google 有時每週會進行多達 70 次發布。

This rapid rate of change provides both the rationale and the opportunity for creating a streamlined launch process. A company that only launches a product every three years doesn’t need a detailed launch process. By the time a new launch occurs, most components of the previously developed launch process will be outdated. Nor do traditional companies have the opportunity to design a detailed launch process, because they don’t accumulate enough experience performing launches to generate a robust and mature process.
這種快速的變革速度為建立一個精簡的發布流程提供了理由和機會。一家每三年才推出一次產品的公司，並不需要一個詳細的發布流程。等到新的發布發生時，先前開發的發布流程的大部分元件都將過時。傳統公司也沒有機會設計一個詳細的發布流程，因為他們沒有累積足夠的發布經驗來產生一個健全和成熟的流程。

# Launch Coordination Engineering
# 發布協調工程 (Launch Coordination Engineering)

Good software engineers have a great deal of expertise in coding and design, and understand the technology of their own products very well. However, the same engineers may be unfamiliar with the challenges and pitfalls of launching a product to millions of users while simultaneously minimizing outages and maximizing performance.
優秀的軟體工程師在編碼和設計方面擁有豐富的專業知識，並且非常了解自己產品的技術。然而，同樣的工程師可能不熟悉向數百萬使用者推出產品，同時又要最小化中斷和最大化效能的挑戰和陷阱。

Google approached the challenges inherent to launches by creating a dedicated consulting team within SRE tasked with the technical side of launching a new product or feature. Staffed by software engineers and systems engineers some with experience in other SRE teams this team specializes in guiding developers toward building reliable and fast products that meet Google’s standards for robustness, scalability, and reliability. This consulting team, Launch Coordination Engineering (LCE), facilitates a smooth launch process in a few ways:
Google 透過在 SRE 內部建立一個專門的諮詢團隊來應對發布所固有的挑戰，該團隊負責推出新產品或功能的技術方面。該團隊由軟體工程師和系統工程師組成——其中一些在其他 SRE 團隊中有經驗——專門指導開發人員建立可靠、快速的產品，以滿足 Google 在穩健性、可擴展性和可靠性方面的標準。這個諮詢團隊，即發布協調工程 (Launch Coordination Engineering, LCE)，透過以下幾種方式促進順暢的發布流程：

Auditing products and services for compliance with Google’s reliability standards and best practices, and providing specific actions to improve reliability Acting as a liaison between the multiple teams involved in a launch Driving the technical aspects of a launch by making sure that tasks maintain momentum Acting as gatekeepers and signing off on launches determined to be "safe" Educating developers on best practices and on how to integrate with Google’s services, equipping them with internal documentation and training resources to speed up their learning
審核產品和服務是否符合 Google 的可靠性標準和最佳實踐，並提供具體行動以提高可靠性、在參與發布的多個團隊之間擔任聯絡人、透過確保任務保持進度來推動發布的技術方面、擔任守門人並簽署被認定為「安全」的發布、教育開發人員最佳實踐以及如何與 Google 的服務整合，為他們提供內部文件和培訓資源以加速他們的學習。

- Auditing products and services for compliance with Google’s reliability standards and best practices, and providing specific actions to improve reliability
- 審核產品和服務是否符合 Google 的可靠性標準和最佳實踐，並提供具體行動以提高可靠性

- Acting as a liaison between the multiple teams involved in a launch
- 在參與發布的多個團隊之間擔任聯絡人

- Driving the technical aspects of a launch by making sure that tasks maintain momentum
- 透過確保任務保持進度來推動發布的技術方面

- Acting as gatekeepers and signing off on launches determined to be "safe"
- 擔任守門人並簽署被認定為「安全」的發布

- Educating developers on best practices and on how to integrate with Google’s services, equipping them with internal documentation and training resources to speed up their learning
- 教育開發人員最佳實踐以及如何與 Google 的服務整合，為他們提供內部文件和培訓資源以加速他們的學習

Members of the LCE team audit services at various times during the service lifecycle. Most audits are conducted before a new product or service launches. If a product development team performs a launch without SRE support, LCE provides the appropriate domain knowledge to ensure a smooth launch. But even products that already have strong SRE support often engage with the LCE team during critical launches. The challenges teams face when launching a new product are substantially different from the day-to-day operation of a reliable service (a task at which SRE teams already excel), and the LCE team can draw on the experience from hundreds of launches. The LCE team also facilitates service audits when new services first engage with SRE.
LCE 團隊的成員在服務生命週期的不同時間對服務進行審核。大多數審核是在新產品或服務推出之前進行的。如果產品開發團隊在沒有 SRE 支援的情況下進行發布，LCE 會提供適當的領域知識以確保順利發布。但即使是已經有強大 SRE 支援的產品，在關鍵發布期間也經常與 LCE 團隊合作。團隊在推出新產品時面臨的挑戰與可靠服務的日常運營（SRE 團隊已經擅長的任務）有很大不同，而 LCE 團隊可以借鑒數百次發布的經驗。當新服務首次與 SRE 合作時，LCE 團隊也會協助進行服務審核。

## The Role of the Launch Coordination Engineer
## 發布協調工程師的角色

Our Launch Coordination Engineering team is composed of Launch Coordination Engineers (LCEs), who are either hired directly into this role, or are SREs with hands-on experience running Google services. LCEs are held to the same technical requirements as any other SRE, and are also expected to have strong communication and leadership skills an LCE brings disparate parties together to work toward a common goal, mediates occasional conflicts, and guides, coaches, and educates fellow engineers.
我們的發布協調工程 (Launch Coordination Engineering) 團隊由發布協調工程師 (LCE) 組成，他們要麼直接被聘用擔任此職位，要麼是具有運行 Google 服務實務經驗的 SRE。LCE 與任何其他 SRE 都遵循相同的技術要求，並且還被期望具備強大的溝通和領導能力——LCE 將不同的各方聚集在一起，共同努力實現一個共同的目標，調解偶爾的衝突，並指導、教練和教育其他工程師。

A team dedicated to coordinating launches offers the following advantages:
一個專門協調發布的團隊提供以下優勢：

Because Launch Coordination Engineer is an SRE role, LCEs are incentivized to prioritize reliability over other concerns. A company that does not share Google’s reliability goals, but shares its rapid rate of change, may choose a different incentive structure.
由於發布協調工程師 (Launch Coordination Engineer) 是一個 SRE 角色，LCE 會被激勵將可靠性置於其他考量之上。一家不共享 Google 可靠性目標，但共享其快速變革速度的公司，可能會選擇不同的激勵結構。

# Setting Up a Launch Process
# 建立發布流程

Google has honed its launch process over a period of more than 10 years. Over time we have identified a number of criteria that characterize a good launch process:
Google 在超過 10 年的時間裡磨練了其發布流程。隨著時間的推移，我們已經確定了許多描述一個良好發布流程的標準：

As you can see, some of these requirements are in obvious conflict. For example, it’s hard to design a process that is simultaneously lightweight and thorough. Balancing these criteria against each other requires continuous work. Google has successfully employed a few tactics to help us achieve these criteria:
如你所見，其中一些要求存在明顯的衝突。例如，很難設計一個既輕量又周全的流程。平衡這些標準需要持續的工作。Google 成功地採用了一些策略來幫助我們實現這些標準：

Experience has demonstrated that engineers are likely to sidestep processes that they consider too burdensome or as adding insufficient value especially when a team is already in crunch mode, and the launch process is seen as just another item blocking their launch. For this reason, LCE must optimize the launch experience continuously to strike the right balance between cost and benefit.
經驗表明，工程師很可能會繞過他們認為過於繁重或附加價值不足的流程——特別是當團隊已經處於緊要關頭，而發布流程被視為只是阻礙他們發布的另一項事務時。因此，LCE 必須持續優化發布體驗，以在成本和效益之間取得適當的平衡。

## The Launch Checklist
## 發布檢查清單

Checklists are used to reduce failure and ensure consistency and completeness across a variety of disciplines. Common examples include aviation preflight checklists and surgical checklists [Gaw09] . Similarly, LCE employs a launch checklist for launch qualification. The checklist ( Launch Coordination Checklist ) helps an LCE assess the launch and provides the launching team with action items and pointers to more information. Here are some examples of items a checklist might include:
檢查清單被用來減少失敗，並確保在各種學科中的一致性和完整性。常見的例子包括航空飛行前檢查清單和手術檢查清單 [Gaw09]。同樣地，LCE 採用一個發布檢查清單來進行發布資格鑑定。該檢查清單（發布協調檢查清單）幫助 LCE 評估發布，並為發布團隊提供行動項目和更多資訊的指引。以下是檢查清單可能包含的一些項目範例：

Question : Do you need a new domain name? Action item : Coordinate with marketing on your desired domain name, and request registration of the domain. Here is a link to the marketing form. Question : Are you storing persistent data? Action item : Make sure you implement backups. Here are instructions for implementing backups. Question : Could a user potentially abuse your service? Action item : Implement rate limiting and quotas. Use the following shared service.
問題：你需要一個新的網域名稱嗎？行動項目：與行銷部門協調你想要的網域名稱，並請求註冊該網域。這裡是行銷表格的連結。問題：你是否儲存持久性資料？行動項目：確保你實作了備份。這裡是實作備份的說明。問題：使用者是否可能濫用你的服務？行動項目：實作速率限制和配額。使用以下共享服務。

- Question : Do you need a new domain name? Action item : Coordinate with marketing on your desired domain name, and request registration of the domain. Here is a link to the marketing form.
- 問題：你需要一個新的網域名稱嗎？ 行動項目：與行銷部門協調你想要的網域名稱，並請求註冊該網域。這裡是行銷表格的連結。

Question : Do you need a new domain name?
問題：你需要一個新的網域名稱嗎？

Action item : Coordinate with marketing on your desired domain name, and request registration of the domain. Here is a link to the marketing form.
行動項目：與行銷部門協調你想要的網域名稱，並請求註冊該網域。這裡是行銷表格的連結。

- Action item : Coordinate with marketing on your desired domain name, and request registration of the domain. Here is a link to the marketing form.
- 行動項目：與行銷部門協調你想要的網域名稱，並請求註冊該網域。這裡是行銷表格的連結。

- Question : Are you storing persistent data? Action item : Make sure you implement backups. Here are instructions for implementing backups.
- 問題：你是否儲存持久性資料？ 行動項目：確保你實作了備份。這裡是實作備份的說明。

Question : Are you storing persistent data?
問題：你是否儲存持久性資料？

Action item : Make sure you implement backups. Here are instructions for implementing backups.
行動項目：確保你實作了備份。這裡是實作備份的說明。

- Action item : Make sure you implement backups. Here are instructions for implementing backups.
- 行動項目：確保你實作了備份。這裡是實作備份的說明。

- Question : Could a user potentially abuse your service? Action item : Implement rate limiting and quotas. Use the following shared service.
- 問題：使用者是否可能濫用你的服務？ 行動項目：實作速率限制和配額。使用以下共享服務。

Question : Could a user potentially abuse your service?
問題：使用者是否可能濫用你的服務？

Action item : Implement rate limiting and quotas. Use the following shared service.
行動項目：實作速率限制和配額。使用以下共享服務。

- Action item : Implement rate limiting and quotas. Use the following shared service.
- 行動項目：實作速率限制和配額。使用以下共享服務。

In practice, there is a near-infinite number of questions to ask about any system, and it is easy for the checklist to grow to an unmanageable size. Maintaining a manageable burden on developers requires careful curation of the checklist. In an effort to curb its growth, at one point, adding new questions to Google’s launch checklist required approval from a vice president. LCE now uses the following guidelines:
在實務上，對於任何系統都有近乎無限多的問題可以問，檢查清單很容易就增長到無法管理的規模。要維持對開發人員可管理的負擔，需要仔細地策劃檢查清單。為了抑制其增長，有一段時間，向 Google 的發布檢查清單中新增問題需要一位副總裁的批准。LCE 現在使用以下指導方針：

Every question’s importance must be substantiated, ideally by a previous launch disaster. Every instruction must be concrete, practical, and reasonable for developers to accomplish.
每個問題的重要性都必須得到證實，最好是透過先前的發布災難。每項指示都必須是具體的、實際的，並且是開發人員可以合理完成的。

- Every question’s importance must be substantiated, ideally by a previous launch disaster.
- 每個問題的重要性都必須得到證實，最好是透過先前的發布災難。

- Every instruction must be concrete, practical, and reasonable for developers to accomplish.
- 每項指示都必須是具體的、實際的，並且是開發人員可以合理完成的。

The checklist needs continuous attention in order to remain relevant and up-to-date: recommendations change over time, internal systems are replaced by different systems, and areas of concern from previous launches become obsolete due to new policies and processes. LCEs curate the checklist continuously and make small updates when team members notice items that need to be modified. Once or twice a year a team member reviews the entire checklist to identify obsolete items, and then works with service owners and subject matter experts to modernize sections of the checklist.
檢查清單需要持續關注以保持其相關性和最新性：建議會隨著時間而改變，內部系統會被不同的系統取代，先前發布中關注的領域會因為新的政策和流程而變得過時。LCE 持續地策劃檢查清單，並在團隊成員注意到需要修改的項目時進行小幅更新。每年一到兩次，團隊成員會審查整個檢查清單以識別過時的項目，然後與服務所有者和主題專家合作，對檢查清單的部分內容進行現代化。

## Driving Convergence and Simplification
## 推動融合與簡化

In a large organization, engineers may not be aware of available infrastructure for common tasks (such as rate limiting). Lacking proper guidance, they’re likely to re-implement existing solutions. Converging on a set of common infrastructure libraries avoids this scenario, and provides obvious benefits to the company: it cuts down on duplicate effort, makes knowledge more easily transferable between services, and results in a higher level of engineering and service quality due to the concentrated attention given to infrastructure.
在一個大型組織中，工程師可能不知道有可用於常見任務（例如速率限制）的基礎設施。缺乏適當的指導，他們很可能會重新實作現有的解決方案。集中使用一套通用的基礎設施函式庫可以避免這種情況，並為公司帶來明顯的好處：它減少了重複的工作，使知識更容易在服務之間轉移，並且由於對基礎設施的集中關注，從而提高了工程和服務的品質。

Almost all groups at Google participate in a common launch process, which makes the launch checklist a vehicle for driving convergence on common infrastructure. Rather than implementing a custom solution, LCE can recommend existing infrastructure as building blocks infrastructure that is already hardened through years of experience and that can help mitigate capacity, performance, or scalability risks. Examples include common infrastructure for rate limiting or user quotas, pushing new data to servers, or releasing new versions of a binary. This type of standardization helped to radically simplify the launch checklist: for example, long sections of the checklist dealing with requirements for rate limiting could be replaced with a single line that stated, "Implement rate limiting using system X."
Google 幾乎所有的團隊都參與一個共同的發布流程，這使得發布檢查清單成為推動通用基礎設施融合的載體。LCE 可以推薦現有的基礎設施作為建構模塊——這些基礎設施已經過多年的經驗強化，可以幫助減輕容量、效能或可擴展性風險——而不是實作客製化的解決方案。例子包括用於速率限制或使用者配額、向伺服器推送新資料或發布新版本二進位檔案的通用基礎設施。這種類型的標準化有助於從根本上簡化發布檢查清單：例如，檢查清單中處理速率限制要求的長篇章節，可以被一行簡單的陳述所取代：「使用系統 X 實作速率限制。」

Due to their breadth of experience across all of Google’s products, LCEs are also in a unique position to identify opportunities for simplification. While working on a launch, they witness the stumbling blocks firsthand: which parts of a launch are causing the most struggle, which steps take a disproportionate amount of time, which problems get solved independently over and over again in similar ways, where common infrastructure is lacking, or where duplication exists in common infrastructure. LCEs have various ways to streamline the launch experience and act as advocates for the launching teams. For example, LCEs might work with the owners of a particularly arduous approval process to simplify their criteria and implement automatic approvals for common cases. LCEs can also escalate pain points to the owners of common infrastructure and create a dialogue with the customers. By leveraging experience gained over the course of multiple previous launches, LCEs can devote more attention to individual concerns and suggestions.
由於他們在 Google 所有產品中擁有廣泛的經驗，LCE 也處於一個獨特的位置，可以識別簡化的機會。在進行發布工作時，他們親眼目睹了絆腳石：發布的哪些部分造成了最大的困難，哪些步驟花費了不成比例的時間，哪些問題以類似的方式被獨立地反覆解決，哪些地方缺乏通用的基礎設施，或者通用的基礎設施中存在重複。LCE 有多種方法來簡化發布體驗，並為發布團隊代言。例如，LCE 可能會與一個特別繁瑣的審批流程的所有者合作，以簡化他們的標準並為常見案例實施自動審批。LCE 還可以將痛點上報給通用基礎設施的所有者，並與客戶建立對話。透過利用在多次先前發布過程中獲得的經驗，LCE 可以更專注於個別的疑慮和建議。

## Launching the Unexpected
## 發布意料之外的事物

When a project enters into a new product space or vertical, an LCE may need to create an appropriate checklist from scratch. Doing so often involves synthesizing experience from relevant domain experts. When drafting a new checklist, it can be helpful to structure the checklist around broad themes such as reliability, failure modes, and processes.
當一個專案進入一個新的產品領域或垂直市場時，LCE 可能需要從頭開始創建一個合適的檢查清單。這樣做通常涉及綜合相關領域專家的經驗。在起草新的檢查清單時，圍繞可靠性、故障模式和流程等廣泛主題來構建檢查清單會很有幫助。

For example, before launching Android, Google had rarely dealt with mass consumer devices with client-side logic that we didn’t directly control. While we can more or less easily fix a bug in Gmail within hours or days by pushing new versions of JavaScript to browsers, such fixes aren’t an option with mobile devices. Therefore, LCEs working on mobile launches engaged mobile domain experts to determine which sections of existing checklists did or did not apply, and where new checklist questions were needed. In such conversations, it’s important to keep the intent of each question in mind in order to avoid mindlessly applying a concrete question or action item that’s not relevant to the design of the unique product being launched. An LCE facing an unusual launch must return to abstract first principles of how to execute a safe launch, then respecialize to make the checklist concrete and useful to developers.
例如，在推出 Android 之前，Google 很少處理我們無法直接控制的、帶有客戶端邏輯的大眾消費性裝置。雖然我們或多或少可以透過向瀏覽器推送新版本的 JavaScript，在數小時或數天內修復 Gmail 中的一個錯誤，但對於行動裝置來說，這樣的修復是不可行的。因此，負責行動裝置發布的 LCE 與行動領域的專家合作，以確定現有檢查清單的哪些部分適用或不適用，以及哪些地方需要新的檢查清單問題。在這樣的對話中，重要的是要記住每個問題的意圖，以避免盲目地應用一個與正在發布的獨特產品設計無關的具體問題或行動項目。面對一個不尋常的發布，LCE 必須回到如何執行安全發布的抽象第一原則，然後重新專業化，使檢查清單對開發人員來說具體而有用。

# Developing a Launch Checklist
# 開發發布檢查清單

A checklist is instrumental to launching new services and products with reproducible reliability. Our launch checklist grew over time and was periodically curated by members of the Launch Coordination Engineering team. The details of a launch checklist will be different for every company, because the specifics must be tailored to a company’s internal services and infrastructure. In the following sections, we extract a number of themes from Google’s LCE checklists and provide examples of how such themes might be fleshed out.
檢查清單對於以可重現的可靠性推出新服務和產品至關重要。我們的發布檢查清單隨著時間的推移而增長，並由發布協調工程團隊的成員定期策劃。每個公司的發布檢查清單的細節都會有所不同，因為具體內容必須根據公司的內部服務和基礎設施進行客製化。在以下各節中，我們從 Google 的 LCE 檢查清單中提取了許多主題，並提供範例說明如何充實這些主題。

## Architecture and Dependencies
## 架構與依賴關係

An architecture review allows you to determine if the service is using shared infrastructure correctly and identifies the owners of shared infrastructure as additional stakeholders in the launch. Google has a large number of internal services that are used as building blocks for new products. During later stages of capacity planning (see [Hix15a] ), the list of dependencies identified in this section of the checklist can be used to make sure that every dependency is correctly provisioned.
架構審查可讓你確定服務是否正確使用共享基礎設施，並將共享基礎設施的所有者識別為發布中的額外利害關係人。Google 有大量內部服務被用作新產品的建構模塊。在容量規劃的後期階段（參見 [Hix15a]），本節檢查清單中識別的依賴項列表可用於確保每個依賴項都已正確配置。

### Example checklist questions
### 檢查清單問題範例

What is your request flow from user to frontend to backend? Are there different types of requests with different latency requirements?
你的請求流程是什麼，從使用者到前端再到後端？是否有不同類型的請求具有不同的延遲要求？

- What is your request flow from user to frontend to backend?
- 你的請求流程是什麼，從使用者到前端再到後端？

- Are there different types of requests with different latency requirements?
- 是否有不同類型的請求具有不同的延遲要求？

### Example action items
### 行動項目範例

Isolate user-facing requests from non user–facing requests. Validate request volume assumptions. One page view can turn into many requests.
將面向使用者的請求與非面向使用者的請求隔離開來。驗證請求量假設。一個頁面瀏覽可能會變成多個請求。

- Isolate user-facing requests from non user–facing requests.
- 將面向使用者的請求與非面向使用者的請求隔離開來。

- Validate request volume assumptions. One page view can turn into many requests.
- 驗證請求量假設。一個頁面瀏覽可能會變成多個請求。

## Integration
## 整合

Many companies’ services run in an internal ecosystem that entails guidelines on how to set up machines, configure new services, set up monitoring, integrate with load balancing, set up DNS addresses, and so forth. These internal ecosystems usually grow over time, and often have their own idiosyncrasies and pitfalls to navigate. Thus, this section of the checklist will vary widely from company to company.
許多公司的服務都在一個內部生態系統中運行，該生態系統包含有關如何設定機器、配置新服務、設定監控、與負載平衡整合、設定 DNS 位址等方面的指導方針。這些內部生態系統通常會隨著時間的推移而增長，並且通常有自己的特性和需要應對的陷阱。因此，檢查清單的這一部分在不同公司之間會有很大差異。

### Example action items
### 行動項目範例

Set up a new DNS name for your service. Set up load balancers to talk to your service. Set up monitoring for your new service.
為你的服務設定一個新的 DNS 名稱。設定負載平衡器以與你的服務通訊。為你的新服務設定監控。

- Set up a new DNS name for your service.
- 為你的服務設定一個新的 DNS 名稱。

- Set up load balancers to talk to your service.
- 設定負載平衡器以與你的服務通訊。

- Set up monitoring for your new service.
- 為你的新服務設定監控。

## Capacity Planning
## 容量規劃

New features may exhibit a temporary increase in usage at launch that subsides within days. The type of workload or traffic mix from a launch spike could be substantially different from steady state, throwing off load test results. Public interest is notoriously hard to predict, and some Google products had to accommodate launch spikes up to 15 times higher than initially estimated. Launching initially in one region or country at a time helps develop the confidence to handle larger launches.
新功能在推出時可能會出現暫時性的使用量增加，並在幾天內消退。發布高峰期的工作負載類型或流量組合可能與穩定狀態有很大不同，從而影響負載測試結果。公眾的興趣出了名地難以預測，一些 Google 產品不得不應對比最初估計高出 15 倍的發布高峰。一次只在一個地區或國家推出，有助於建立處理更大規模發布的信心。

Capacity interacts with redundancy and availability. For instance, if you need three replicated deployments to serve 100% of your traffic at peak, you need to maintain four or five deployments, one or two of which are redundant, in order to shield users from maintenance and unexpected malfunctions. Datacenter and network resources often have a long lead time and need to be requested far enough in advance for your company to obtain them.
容量與冗餘和可用性相互作用。例如，如果你需要三個複製的部署來為你的高峰期流量提供 100% 的服務，你就需要維護四到五個部署，其中一到兩個是冗餘的，以便保護使用者免受維護和意外故障的影響。資料中心和網路資源通常有很長的交付週期，需要提前足夠長的時間提出請求，以便你的公司能夠獲得它們。

### Example checklist questions
### 檢查清單問題範例

Is this launch tied to a press release, advertisement, blog post, or other form of promotion? How much traffic and rate of growth do you expect during and after the launch? Have you obtained all the compute resources needed to support your traffic?
這次發布是否與新聞稿、廣告、部落格文章或其他形式的宣傳活動有關？你預計在發布期間和之後的流量和增長率是多少？你是否已經獲得了支援你流量所需的所有計算資源？

- Is this launch tied to a press release, advertisement, blog post, or other form of promotion?
- 這次發布是否與新聞稿、廣告、部落格文章或其他形式的宣傳活動有關？

- How much traffic and rate of growth do you expect during and after the launch?
- 你預計在發布期間和之後的流量和增長率是多少？

- Have you obtained all the compute resources needed to support your traffic?
- 你是否已經獲得了支援你流量所需的所有計算資源？

## Failure Modes
## 故障模式

A systematic look at the possible failure modes of a new service ensures high reliability from the start. In this portion of the checklist, examine each component and dependency and identify the impact of its failure. Can the service deal with individual machine failures? Datacenter outages? Network failures? How do we deal with bad input data? Are we prepared for the possibility of a denial-of-service (DoS) attack? Can the service continue serving in degraded mode if one of its dependencies fails? How do we deal with unavailability of a dependency upon startup of the service? During runtime?
從一開始就系統性地審視新服務可能的故障模式，可以確保高可靠性。在檢查清單的這一部分，檢查每個元件和依賴項，並確定其故障的影響。服務能否處理單個機器的故障？資料中心中斷？網路故障？我們如何處理不良的輸入資料？我們是否為拒絕服務 (DoS) 攻擊的可能性做好了準備？如果其中一個依賴項失敗，服務能否在降級模式下繼續提供服務？我們如何處理服務啟動時依賴項不可用的情況？執行期間呢？

### Example checklist questions
### 檢查清單問題範例

Do you have any single points of failure in your design? How do you mitigate unavailability of your dependencies?
你的設計中是否有任何單點故障 (single points of failure)？你如何緩解你的依賴項不可用的情況？

- Do you have any single points of failure in your design?
- 你的設計中是否有任何單點故障 (single points of failure)？

- How do you mitigate unavailability of your dependencies?
- 你如何緩解你的依賴項不可用的情況？

### Example action items
### 行動項目範例

Implement request deadlines to avoid running out of resources for long-running requests. Implement load shedding to reject new requests early in overload situations.
實作請求截止日期，以避免長時間運行的請求耗盡資源。實作負載調節 (load shedding)，以便在過載情況下及早拒絕新請求。

- Implement request deadlines to avoid running out of resources for long-running requests.
- 實作請求截止日期，以避免長時間運行的請求耗盡資源。

- Implement load shedding to reject new requests early in overload situations.
- 實作負載調節 (load shedding)，以便在過載情況下及早拒絕新請求。

## Client Behavior
## 客戶端行為

On a traditional website, there is rarely a need to take abusive behavior from legitimate users into account. When every request is triggered by a user action such as a click on a link, the request rates are limited by how quickly users can click. To double the load, the number of users would have to double.
在傳統網站上，很少需要考慮來自合法使用者的濫用行為。當每個請求都是由使用者操作（例如點擊連結）觸發時，請求速率受使用者點擊速度的限制。要使負載加倍，使用者數量就必須加倍。

This axiom no longer holds when we consider clients that initiate actions without user input for example, a cell phone app that periodically syncs its data into the cloud, or a website that periodically refreshes. In either of these scenarios, abusive client behavior can very easily threaten the stability of a service. (There is also the topic of protecting a service from abusive traffic such as scrapers and denial-of-service attacks which is different from designing safe behavior for first-party clients.)
當我們考慮在沒有使用者輸入的情況下啟動操作的客戶端時，這個公理就不再成立了——例如，一個定期將其資料同步到雲端的手機應用程式，或者一個定期刷新的網站。在這兩種情況下，濫用的客戶端行為都非常容易威脅到服務的穩定性。（還有一個議題是保護服務免受濫用流量的影響，例如爬蟲和拒絕服務攻擊——這與為第一方客戶端設計安全行為是不同的。）

### Example checklist question
### 檢查清單問題範例

Do you have auto-save/auto-complete/heartbeat functionality?
你是否有自動儲存/自動完成/心跳功能？

- Do you have auto-save/auto-complete/heartbeat functionality?
- 你是否有自動儲存/自動完成/心跳功能？

### Example action items
### 行動項目範例

Make sure that your client backs off exponentially on failure. Make sure that you jitter automatic requests.
確保你的客戶端在失敗時會指數級退避。確保你對自動請求進行了抖動 (jitter)。

- Make sure that your client backs off exponentially on failure.
- 確保你的客戶端在失敗時會指數級退避。

- Make sure that you jitter automatic requests.
- 確保你對自動請求進行了抖動 (jitter)。

## Processes and Automation
## 流程與自動化

Google encourages engineers to use standard tools to automate common processes. However, automation is never perfect, and every service has processes that need to be executed by a human: creating a new release, moving the service to a different data center, restoring data from backups, and so on. For reliability reasons, we strive to minimize single points of failure, which include humans.
Google 鼓勵工程師使用標準工具來自動化常見流程。然而，自動化從來都不是完美的，每個服務都有需要由人來執行的流程：建立新版本、將服務遷移到不同的資料中心、從備份中還原資料等等。出於可靠性的原因，我們努力最小化單點故障，其中包括人。

These remaining processes should be documented before launch to ensure that the information is translated from an engineer’s mind onto paper while it is still fresh, and that it is available in an emergency. Processes should be documented in such a way that any team member can execute a given process in an emergency.
這些剩餘的流程應在發布前被記錄下來，以確保資訊在工程師的腦海中還很新鮮時就被轉移到紙上，並且在緊急情況下可用。流程的記錄方式應該是，任何團隊成員都可以在緊急情況下執行給定的流程。

### Example checklist question
### 檢查清單問題範例

Are there any manual processes required to keep the service running?
是否有任何手動流程是維持服務運行所必需的？

- Are there any manual processes required to keep the service running?
- 是否有任何手動流程是維持服務運行所必需的？

### Example action items
### 行動項目範例

Document all manual processes. Document the process for moving your service to a new datacenter. Automate the process for building and releasing a new version.
記錄所有手動流程。記錄將你的服務遷移到新資料中心的流程。自動化建立和發布新版本的流程。

- Document all manual processes.
- 記錄所有手動流程。

- Document the process for moving your service to a new datacenter.
- 記錄將你的服務遷移到新資料中心的流程。

- Automate the process for building and releasing a new version.
- 自動化建立和發布新版本的流程。

## Development Process
## 開發流程

Google is an extensive user of version control, and almost all development processes are deeply integrated with the version control system. Many of our best practices revolve around how to use the version control system effectively. For example, we perform most development on the mainline branch, but releases are built on separate branches per release. This setup makes it easy to fix bugs in a release without pulling in unrelated changes from the mainline.
Google 廣泛使用版本控制，幾乎所有的開發流程都與版本控制系統深度整合。我們的許多最佳實踐都圍繞著如何有效地使用版本控制系統。例如，我們的大部分開發工作都在主線分支上進行，但發布版本則是在每個版本獨立的分支上建立的。這種設定使得在發布版本中修復錯誤變得容易，而不會引入主線中不相關的變更。

Google also uses version control for other purposes, such as storing configuration files. Many of the advantages of version control history tracking, attributing changes to individuals, and code reviews apply to configuration files as well. In some cases, we also propagate changes from the version control system to the live servers automatically, so that an engineer only needs to submit a change to make it go live.
Google 也將版本控制用於其他目的，例如儲存設定檔。版本控制的許多優點——歷史追蹤、將變更歸因於個人以及程式碼審查——也適用於設定檔。在某些情況下，我們還會自動將變更從版本控制系統傳播到即時伺服器，因此工程師只需要提交一個變更即可使其生效。

### Example action items
### 行動項目範例

Check all code and configuration files into the version control system. Cut each release on a new release branch.
將所有程式碼和設定檔簽入版本控制系統。在新的發布分支上剪下每個版本。

- Check all code and configuration files into the version control system.
- 將所有程式碼和設定檔簽入版本控制系統。

- Cut each release on a new release branch.
- 在新的發布分支上剪下每個版本。

## External Dependencies
## 外部依賴

Sometimes a launch depends on factors beyond company control. Identifying these factors allows you to mitigate the unpredictability they entail. For instance, the dependency may be a code library maintained by third parties, or a service or data provided by another company. When a vendor outage, bug, systematic error, security issue, or unexpected scalability limit actually occurs, prior planning will enable you to avert or mitigate damage to your users. In Google’s history of launches, we’ve used filtering and/or rewriting proxies, data transcoding pipelines, and caches to mitigate some of these risks.
有時，一次發布取決於公司無法控制的因素。識別這些因素可以讓你減輕它們所帶來的不確定性。例如，依賴項可能是一個由第三方維護的程式碼庫，或者是由另一家公司提供的服務或資料。當供應商發生中斷、錯誤、系統性錯誤、安全問題或意外的可擴展性限制時，事先的規劃將使你能夠避免或減輕對使用者的損害。在 Google 的發布歷史中，我們曾使用過濾和/或重寫代理、資料轉碼管道和快取來減輕其中一些風險。

### Example checklist questions
### 檢查清單問題範例

What third-party code, data, services, or events does the service or the launch depend upon? Do any partners depend on your service? If so, do they need to be notified of your launch? What happens if you or the vendor can’t meet a hard launch deadline?
服務或發布依賴哪些第三方程式碼、資料、服務或事件？是否有任何合作夥伴依賴你的服務？如果是，他們是否需要被通知你的發布？如果你或供應商無法在硬性發布截止日期前完成會怎麼樣？

- What third-party code, data, services, or events does the service or the launch depend upon?
- 服務或發布依賴哪些第三方程式碼、資料、服務或事件？

- Do any partners depend on your service? If so, do they need to be notified of your launch?
- 是否有任何合作夥伴依賴你的服務？如果是，他們是否需要被通知你的發布？

- What happens if you or the vendor can’t meet a hard launch deadline?
- 如果你或供應商無法在硬性發布截止日期前完成會怎麼樣？

## Rollout Planning
## 部署規劃

In large distributed systems, few events happen instantaneously. For reasons of reliability, such immediacy isn’t usually ideal anyway. A complicated launch might require enabling individual features on a number of different subsystems, and each of those configuration changes might take hours to complete. Having a working configuration in a test instance doesn’t guarantee that the same configuration can be rolled out to the live instance. Sometimes a complicated dance or special functionality is required to make all components launch cleanly and in the correct order.
在大型分散式系統中，很少有事件是瞬間發生的。出於可靠性的原因，這種即時性通常也不是理想的。一個複雜的發布可能需要在許多不同的子系統上啟用個別功能，而每個設定變更可能需要數小時才能完成。在測試實例中擁有一個可行的設定，並不能保證相同的設定可以部署到即時實例中。有時，需要一個複雜的協調或特殊功能，才能讓所有元件乾淨地、按正確的順序啟動。

External requirements from teams like marketing and PR might add further complications. For example, a team might need a feature to be available in time for the keynote at a conference, but need to keep the feature invisible before the keynote.
來自市場和公關等團隊的外部要求可能會增加更多的複雜性。例如，一個團隊可能需要一個功能在會議的主題演講時可用，但又需要在主題演講之前保持該功能的不可見。

Contingency measures are another part of rollout planning. What if you don’t manage to enable the feature in time for the keynote? Sometimes these contingency measures are as simple as preparing a backup slide deck that says, "We will be launching this feature over the next days" rather than "We have launched this feature."
應變措施是部署規劃的另一部分。如果你沒能在主題演講前及時啟用該功能怎麼辦？有時，這些應變措施就像準備一套備用投影片一樣簡單，上面寫著：「我們將在未來幾天內推出此功能」，而不是「我們已經推出了此功能」。

### Example action items
### 行動項目範例

Set up a launch plan that identifies actions to take to launch the service. Identify who is responsible for each item. Identify risk in the individual launch steps and implement contingency measures.
建立一個發布計畫，確定啟動服務所需採取的行動。確定每個項目的負責人。識別個別發布步驟中的風險並實施應變措施。

- Set up a launch plan that identifies actions to take to launch the service. Identify who is responsible for each item.
- 建立一個發布計畫，確定啟動服務所需採取的行動。確定每個項目的負責人。

- Identify risk in the individual launch steps and implement contingency measures.
- 識別個別發布步驟中的風險並實施應變措施。

# Selected Techniques for Reliable Launches
# 可靠發布的精選技術

As described in other parts of this book, Google has developed a number of techniques for running reliable systems over the years. Some of these techniques are particularly well suited to launching products safely. They also provide advantages during regular operation of the service, but it’s particularly important to get them right during the launch phase.
正如本書其他部分所述，多年來 Google 開發了許多運行可靠系統的技術。其中一些技術特別適合安全地推出產品。它們在服務的常規運營期間也提供了優勢，但在發布階段正確地使用它們尤為重要。

## Gradual and Staged Rollouts
## 漸進式與分階段部署

One adage of system administration is "never change a running system." Any change represents risk, and risk should be minimized in order to assure reliability of a system. What’s true for any small system is doubly true for highly replicated, globally distributed systems like those run by Google.
系統管理的一句格言是「永遠不要改變一個正在運行的系統」。任何改變都代表著風險，為了確保系統的可靠性，風險應該被最小化。對任何小型系統來說是如此，對像 Google 運行的那樣高度複製、全球分佈的系統來說更是如此。

Very few launches at Google are of the "push-button" variety, in which we launch a new product at a specific time for the entire world to use. Over time, Google has developed a number of patterns that allow us to launch products and features gradually and thereby minimize risk; see A Collection of Best Practices for Production Services .
Google 很少有「按鈕式」的發布，即我們在特定時間為全世界推出一個新產品。隨著時間的推移，Google 已經開發出許多模式，讓我們能夠逐步推出產品和功能，從而將風險降至最低；請參閱「生產服務最佳實踐集」。

Almost all updates to Google’s services proceed gradually, according to a defined process, with appropriate verification steps interspersed. A new server might be installed on a few machines in one datacenter and observed for a defined period of time. If all looks well, the server is installed on all machines in one datacenter, observed again, and then installed on all machines globally. The first stages of a rollout are usually called "canaries” an allusion to canaries carried by miners into a coal mine to detect dangerous gases. Our canary servers detect dangerous effects from the behavior of the new software under real user traffic.
幾乎所有對 Google 服務的更新都是根據一個定義好的流程逐步進行的，其中穿插著適當的驗證步驟。一個新的伺服器可能會先安裝在一個資料中心的幾台機器上，並在一段定義好的時間內進行觀察。如果一切看起來都很好，伺服器就會安裝在該資料中心的所有機器上，再次觀察，然後再安裝在全球所有的機器上。部署的最初階段通常被稱為「金絲雀 (canaries)」，這是對礦工帶入煤礦中以偵測危險氣體的金絲雀的暗喻。我們的金絲雀伺服器在真實使用者流量下偵測新軟體行為所帶來的危險影響。

Canary testing is a concept embedded into many of Google’s internal tools used to make automated changes, as well as for systems that change configuration files. Tools that manage the installation of new software typically observe the newly started server for a while, making sure that the server doesn’t crash or otherwise misbehave. If the change doesn’t pass the validation period, it’s automatically rolled back.
金絲雀測試 (Canary testing) 是一個嵌入在 Google 許多內部工具中的概念，這些工具用於進行自動化變更，也用於變更設定檔的系統。管理新軟體安裝的工具通常會觀察新啟動的伺服器一段時間，確保伺服器不會崩潰或出現其他不當行為。如果變更沒有通過驗證期，它會被自動回復。

The concept of gradual rollouts even applies to software that does not run on Google’s servers. New versions of an Android app can be rolled out in a gradual manner, in which the updated version is offered to a subset of the installs for upgrade. The percentage of upgraded instances gradually increases over time until it reaches 100%. This type of rollout is particularly helpful if the new version results in additional traffic to the backend servers in Google’s datacenters. This way, we can observe the effect on our servers as we gradually roll out the new version and detect problems early.
漸進式部署 (gradual rollouts) 的概念甚至適用於不在 Google 伺服器上運行的軟體。新版本的 Android 應用程式可以以漸進的方式推出，其中更新的版本會提供給一部分安裝進行升級。升級實例的百分比會隨著時間逐漸增加，直到達到 100%。如果新版本會導致對 Google 資料中心後端伺服器的額外流量，這種部署方式特別有幫助。這樣，我們可以在逐步推出新版本的過程中觀察對我們伺服器的影響，並及早發現問題。

The invite system is another type of gradual rollout. Frequently, rather than allowing free signups to a new service, only a limited number of users are allowed to sign up per day. Rate-limited signups are often coupled with an invite system, in which a user can send a limited number of invites to friends.
邀請系統是另一種漸進式部署 (gradual rollout)。通常，與其允許自由註冊新服務，不如每天只允許有限數量的使用者註冊。速率限制的註冊通常與邀請系統相結合，在該系統中，使用者可以向朋友發送有限數量的邀請。

## Feature Flag Frameworks
## 功能旗標框架

Google often augments prelaunch testing with strategies that mitigate the risk of an outage. A mechanism to roll out changes slowly, allowing for observation of total system behavior under real workloads, can pay for its engineering investment in reliability, engineering velocity, and time to market. These mechanisms have proven particularly useful in cases where realistic test environments are impractical, or for particularly complex launches for which the effects can be hard to predict.
Google 通常會用一些策略來增強發布前的測試，以減輕中斷的風險。一個能夠緩慢推出變更，並允許在真實工作負載下觀察整個系統行為的機制，可以在可靠性、工程速度和上市時間方面為其工程投資帶來回報。這些機制在測試環境不切實際，或對於效果難以預測的特別複雜的發布情況下，已被證明特別有用。

Furthermore, not all changes are equal. Sometimes you simply want to check whether a small tweak to the user interface improves the experience of your users. Such small changes shouldn’t involve thousands of lines of code or a heavyweight launch process. You may want to test hundreds of such changes in parallel.
此外，並非所有的變更都是平等的。有時你只是想檢查一下對使用者介面的微小調整是否能改善使用者的體驗。這樣的小變更不應該涉及數千行程式碼或一個繁重的發布流程。你可能想並行測試數百個這樣的變更。

Finally, sometimes you want to find out whether a small sample of users like using an early prototype of a new, hard-to-implement feature. You don’t want to spend months of engineering effort to harden a new feature to serve millions of users, only to find that the feature is a flop.
最後，有時你想知道一小部分使用者是否喜歡使用一個難以實現的新功能的早期原型。你不想花費數月的工程精力來強化一個新功能以服務數百萬使用者，結果卻發現這個功能是個失敗品。

To accommodate the preceding scenarios, several Google products devised feature flag frameworks. Some of those frameworks were designed to roll out new features gradually from 0% to 100% of users. Whenever a product introduced any such framework, the framework itself was hardened as much as possible so that most of its applications would not need any LCE involvement. Such frameworks usually meet the following requirements:
為了因應上述情境，一些 Google 產品設計了功能旗標 (feature flag) 框架。其中一些框架被設計用來將新功能從 0% 逐步推廣到 100% 的使用者。每當一個產品引入任何這樣的框架時，框架本身都會被盡可能地強化，這樣它的大多數應用程式就不需要任何 LCE 的參與。這樣的框架通常滿足以下要求：

Roll out many changes in parallel, each to a few servers, users, entities, or datacenters Gradually increase to a larger but limited group of users, usually between 1 and 10 percent Direct traffic through different servers depending on users, sessions, objects, and/or locations Automatically handle failure of the new code paths by design, without affecting users Independently revert each such change immediately in the event of serious bugs or side effects Measure the extent to which each change improves the user experience
並行推出多個變更，每個變更針對少數伺服器、使用者、實體或資料中心；逐步增加到一個更大但有限的使用者群組，通常在 1% 到 10% 之間；根據使用者、會話、物件和/或位置將流量導向不同的伺服器；透過設計自動處理新程式碼路徑的失敗，而不影響使用者；在發生嚴重錯誤或副作用時，立即獨立地回復每個此類變更；衡量每個變更在多大程度上改善了使用者體驗。

- Roll out many changes in parallel, each to a few servers, users, entities, or datacenters
- 並行推出多個變更，每個變更針對少數伺服器、使用者、實體或資料中心

- Gradually increase to a larger but limited group of users, usually between 1 and 10 percent
- 逐步增加到一個更大但有限的使用者群組，通常在 1% 到 10% 之間

- Direct traffic through different servers depending on users, sessions, objects, and/or locations
- 根據使用者、會話、物件和/或位置將流量導向不同的伺服器

- Automatically handle failure of the new code paths by design, without affecting users
- 透過設計自動處理新程式碼路徑的失敗，而不影響使用者

- Independently revert each such change immediately in the event of serious bugs or side effects
- 在發生嚴重錯誤或副作用時，立即獨立地回復每個此類變更

- Measure the extent to which each change improves the user experience
- 衡量每個變更在多大程度上改善了使用者體驗

Google’s feature flag frameworks fall into two general classes:
Google 的功能旗標 (feature flag) 框架大致分為兩類：

Those that primarily facilitate user interface improvements Those that support arbitrary server-side and business logic changes
主要促進使用者介面改進的、支援任意伺服器端和業務邏輯變更的。

- Those that primarily facilitate user interface improvements
- 主要促進使用者介面改進的

- Those that support arbitrary server-side and business logic changes
- 支援任意伺服器端和業務邏輯變更的

The simplest feature flag framework for user interface changes in a stateless service is an HTTP payload rewriter at frontend application servers, limited to a subset of cookies or another similar HTTP request/response attribute. A configuration mechanism may specify an identifier associated with the new code paths and the scope of the change (e.g., cookie hash mod range), whitelists, and blacklists.
對於無狀態服務中的使用者介面變更，最簡單的功能旗標 (feature flag) 框架是在前端應用程式伺服器上的一個 HTTP 負載重寫器，限制在一部分 cookie 或其他類似的 HTTP 請求/回應屬性。一個設定機制可以指定與新程式碼路徑相關聯的識別碼以及變更的範圍（例如，cookie 雜湊模數範圍）、白名單和黑名單。

Stateful services tend to limit feature flags to a subset of unique logged-in user identifiers or to the actual product entities accessed, such as the ID of documents, spreadsheets, or storage objects. Rather than rewrite HTTP payloads, stateful services are more likely to proxy or reroute requests to different servers depending on the change, conferring the ability to test improved business logic and more
      complex new features.
有狀態的服務傾向於將功能旗標 (feature flags) 限制在一部分唯一的已登入使用者識別碼或實際存取的產品實體上，例如文件、試算表或儲存物件的 ID。有狀態的服務更有可能根據變更將請求代理或重新路由到不同的伺服器，而不是重寫 HTTP 負載，從而賦予測試改進的業務邏輯和更複雜新功能的能力。

## Dealing with Abusive Client Behavior
## 處理濫用客戶端行為

The simplest example of abusive client behavior is a misjudgment of update rates. A new client that syncs every 60 seconds, as opposed to every 600 seconds, causes 10 times the load on the service. Retry behavior has a number of pitfalls that affect user-initiated requests, as well as client-initiated requests. Take the example of a service that is overloaded and is therefore failing some requests: if the clients retry the failed requests, they add load to an already overloaded service, resulting in more retries and even more requests. Instead, clients need to reduce the frequency of retries, usually by adding exponentially increasing delay between retries, in addition to carefully considering the types of errors that warrant a retry. For example, a network error usually warrants a retry, but a 4xx HTTP error (which indicates an error on the client’s side) usually does not.
濫用客戶端行為最簡單的例子是對更新速率的誤判。一個每 60 秒同步一次的新客戶端，相較於每 600 秒同步一次，會對服務造成 10 倍的負載。重試行為有許多陷阱，會影響使用者發起的請求以及客戶端發起的請求。舉個例子，一個服務過載，因此某些請求失敗：如果客戶端重試失敗的請求，它們會增加已經過載的服務的負載，導致更多的重試和更多的請求。相反地，客戶端需要降低重試的頻率，通常是在重試之間增加指數級增長的延遲，此外還要仔細考慮哪些類型的錯誤值得重試。例如，網路錯誤通常值得重試，但 4xx HTTP 錯誤（表示客戶端方面的錯誤）通常不值得。

Intentional or inadvertent synchronization of automated requests in a thundering herd (much like those described in Chapters Distributed Periodic Scheduling with Cron and Data Processing Pipelines ) is another common example of abusive client behavior. A phone app developer might decide that 2 a.m. is a good time to download updates, because the user is most likely asleep and won’t be inconvenienced by the download. However, such a design results in a barrage of requests to the download server at 2 a.m. every night, and almost no requests at any other time. Instead, every client should choose the time for this type of request randomly .
有意或無意地同步自動化請求，造成「驚群效應 (thundering herd)」（很像在「分散式定期排程與 Cron」和「資料處理管道」章節中描述的那樣），是濫用客戶端行為的另一個常見例子。一個手機應用程式開發者可能會認為凌晨 2 點是下載更新的好時機，因為使用者很可能在睡覺，不會被下載打擾。然而，這樣的設計會導致每天凌晨 2 點對下載伺服器的大量請求，而在其他任何時間幾乎沒有請求。相反地，每個客戶端應該隨機選擇這類請求的時間。

Randomness also needs to be injected into other periodic processes. To return to the previously mentioned retries: let’s take the example of a client that sends a request, and when it encounters a failure, retries after 1 second, then 2 seconds, then 4 seconds, and so on. Without randomness, a brief request spike that leads to an increased error rate could repeat itself due to retries after 1 second, then 2 seconds, then 4 seconds. In order to even out these synchronized events, each delay needs to be jittered (that is, adjusted by a random amount).
隨機性也需要被注入到其他週期性流程中。回到前面提到的重試：讓我們舉一個客戶端發送請求的例子，當它遇到失敗時，它會在 1 秒、然後 2 秒、然後 4 秒後重試，依此類推。如果沒有隨機性，一個導致錯誤率增加的短暫請求高峰，可能會因為在 1 秒、然後 2 秒、然後 4 秒後的重試而重複出現。為了平滑這些同步事件，每個延遲都需要被抖動 (jittered)（也就是說，用一個隨機量進行調整）。

The ability to control the behavior of a client from the server side has proven an important tool in the past. For an app on a device, such control might mean instructing the client to check in periodically with the server and download a configuration file. The file might enable or disable certain features or set parameters, such as how often the client syncs or how often it retries.
從伺服器端控制客戶端行為的能力，在過去已被證明是一個重要的工具。對於裝置上的應用程式，這種控制可能意味著指示客戶端定期向伺服器報到並下載一個設定檔。該檔案可以啟用或禁用某些功能，或設定參數，例如客戶端同步的頻率或重試的頻率。

The client configuration might even enable completely new user-facing functionality. By hosting the code that supports new functionality in the client application before we activate that feature, we greatly reduce the risk associated with a launch. Releasing a new version becomes much easier if we don’t need to maintain parallel release tracks for a version with the new functionality versus without the functionality. This holds particularly true if we’re not dealing with a single piece of new functionality, but a set of independent features that might be released on different schedules, which would necessitate maintaining a combinatorial explosion of different versions.
客戶端設定甚至可以啟用全新的面向使用者的功能。透過在我們啟用新功能之前，就在客戶端應用程式中託管支援該功能的程式碼，我們大大降低了與發布相關的風險。如果我們不需要為有新功能的版本和沒有新功能的版本維護平行的發布軌道，那麼發布新版本就會變得容易得多。如果我們處理的不是單一的新功能，而是一組可能在不同時間表上發布的獨立功能，這點尤其適用，因為這將需要維護一個組合爆炸的不同版本。

Having this sort of dormant functionality also makes aborting launches easier when adverse effects are discovered during a rollout. In such cases, we can simply switch the feature off, iterate, and release an updated version of the app. Without this type of client configuration, we would have to provide a new version of the app without the feature, and update the app on all users’ phones.
擁有這種潛伏功能，在部署過程中發現不良影響時，也更容易中止發布。在這種情況下，我們可以簡單地關閉該功能，進行迭代，然後發布一個更新版本的應用程式。如果沒有這種類型的客戶端設定，我們就必須提供一個沒有該功能的新版本應用程式，並在所有使用者的手機上更新該應用程式。

## Overload Behavior and Load Tests
## 過載行為與負載測試

Overload situations are a particularly complex failure mode, and therefore deserve additional attention. Runaway success is usually the most welcome cause of overload when a new service launches, but there are myriad other causes, including load balancing failures, machine outages, synchronized client behavior, and external attacks.
過載情況是一種特別複雜的故障模式，因此值得額外關注。當新服務推出時，失控的成功通常是過載最受歡迎的原因，但還有無數其他原因，包括負載平衡故障、機器停機、同步的客戶端行為和外部攻擊。

A naive model assumes that CPU usage on a machine providing a particular service scales linearly with the load (for example, number of requests or amount of data processed), and once available CPU is exhausted, processing simply becomes slower. Unfortunately, services rarely behave in this ideal fashion in the real world. Many services are much slower when they are not loaded, usually due to the effect of various kinds of caches such as CPU caches, JIT caches, and service-specific data caches. As load increases, there is usually a window in which CPU usage and load on the service correspond linearly, and response times stay mostly constant.
一個天真的模型假設，提供特定服務的機器的 CPU 使用率會隨著負載（例如，請求數量或處理的資料量）線性擴展，一旦可用的 CPU 耗盡，處理速度只會變慢。不幸的是，在現實世界中，服務很少以這種理想的方式運作。許多服務在沒有負載時速度要慢得多，這通常是由於各種快取（例如 CPU 快取、JIT 快取和特定於服務的資料快取）的影響。隨著負載的增加，通常會有一個窗口，其中 CPU 使用率和服務上的負載呈線性對應，且回應時間大多保持不變。

At some point, many services reach a point of nonlinearity as they approach overload. In the most benign cases, response times simply begin to increase, resulting in a degraded user experience but not necessarily causing an outage (although a slow dependency might cause user-visible errors up the stack, due to exceeded RPC deadlines). In the most drastic cases, a service locks up completely in response to overload .
在某個時候，許多服務在接近過載時會達到一個非線性的點。在最良性的情況下，回應時間只是開始增加，導致使用者體驗下降，但不一定會造成中斷（儘管一個緩慢的依賴項可能會因為超過 RPC 截止時間而在上游引起使用者可見的錯誤）。在最嚴重的情況下，服務會因過載而完全鎖死。

To cite a specific example of overload behavior: a service logged debugging information in response to backend errors. It turned out that logging debugging information was more expensive than handling the backend response in a normal case. Therefore, as the service became overloaded and timed out backend responses inside its own RPC stack, the service spent even more CPU time logging these responses, timing out more requests in the meantime until the service ground to a complete halt. In services running on the Java Virtual Machine (JVM), a similar effect of grinding to a halt is sometimes called "GC (garbage collection) thrashing." In this scenario, the virtual machine’s internal memory management runs in increasingly closer cycles, trying to free up memory until most of the CPU time is consumed by memory management.
舉一個過載行為的具體例子：一個服務在回應後端錯誤時會記錄偵錯資訊。結果發現，記錄偵錯資訊比在正常情況下處理後端回應更昂貴。因此，當服務變得過載並在其自身的 RPC 堆疊內逾時後端回應時，該服務花費了更多的 CPU 時間來記錄這些回應，同時逾時了更多的請求，直到服務完全停止。在運行在 Java 虛擬機器 (JVM) 上的服務中，類似的停頓效應有時被稱為「GC（垃圾回收）顛簸 (thrashing)」。在這種情況下，虛擬機器的內部記憶體管理以越來越近的週期運行，試圖釋放記憶體，直到大部分 CPU 時間都被記憶體管理消耗掉。

Unfortunately, it is very hard to predict from first principles how a service will react to overload. Therefore, load tests are an invaluable tool, both for reliability reasons and capacity planning, and load testing is required for most launches.
不幸的是，很難從第一性原理預測一個服務將如何應對過載。因此，負載測試是一個非常寶貴的工具，無論是出於可靠性原因還是容量規劃，大多數發布都需要進行負載測試。

# Development of LCE
# LCE 的發展

In Google’s formative years, the size of the engineering team doubled every year for several years in a row, fragmenting the engineering department into many small teams working on many experimental new products and features. In such a climate, novice engineers run the risk of repeating the mistakes of their predecessors, especially when it comes to launching new features and products successfully.
在 Google 的 formative years，工程團隊的規模連續幾年每年翻倍，將工程部門分散成許多小團隊，從事許多實驗性的新產品和功能。在這樣的氛圍下，新手工程師冒著重蹈前人覆轍的風險，尤其是在成功推出新功能和產品方面。

To mitigate the repetition of such mistakes by capturing the lessons learned from past launches, a small band of experienced engineers, called the "Launch Engineers," volunteered to act as a consulting team. The Launch Engineers developed checklists for new product launches, covering topics such as:
為了透過汲取過去發布的經驗教訓來減輕這種錯誤的重複，一小群經驗豐富的工程師，被稱為「發布工程師」，自願擔任諮詢團隊。發布工程師為新產品發布制定了檢查清單，涵蓋了諸如以下主題：

When to consult with the legal department How to select domain names How to register new domains without misconfiguring DNS Common engineering design and production deployment pitfalls
何時諮詢法律部門、如何選擇網域名稱、如何註冊新網域而不錯誤配置 DNS、常見的工程設計和生產部署陷阱。

- When to consult with the legal department
- 何時諮詢法律部門

- How to select domain names
- 如何選擇網域名稱

- How to register new domains without misconfiguring DNS
- 如何註冊新網域而不錯誤配置 DNS

- Common engineering design and production deployment pitfalls
- 常見的工程設計和生產部署陷阱

"Launch Reviews," as the Launch Engineers’ consulting sessions came to be called, became a common practice days to weeks before the launch of many new products.
「發布審查」，正如發布工程師的諮詢會議後來被稱呼的那樣，在許多新產品發布前的數天到數週成為一種普遍的做法。

Within two years, the product deployment requirements in the launch checklist grew long and complex. Combined with the increasing complexity of Google’s deployment environment, it became more and more challenging for product engineers to stay up-to-date on how to make changes safely. At the same time, the SRE organization was growing quickly, and inexperienced SREs were sometimes overly cautious and averse to change. Google ran a risk that the resulting negotiations between these two parties would reduce the velocity of product/feature launches.
在兩年內，發布檢查清單中的產品部署要求變得又長又複雜。再加上 Google 部署環境日益複雜，產品工程師要跟上如何安全地進行變更的最新資訊變得越來越具挑戰性。與此同時，SRE 組織正在迅速發展，沒有經驗的 SRE 有時過於謹慎，不願改變。Google 面臨著一個風險，即這兩方之間的協商可能會降低產品/功能發布的速度。

To mitigate this scenario from the engineering perspective, SRE staffed a small, full-time team of LCEs in 2004. They were responsible for accelerating the launches of new products and features, while at the same time applying SRE expertise to ensure that Google shipped reliable products with high availability and low latency.
為了從工程角度緩解這種情況，SRE 在 2004 年配備了一個小型的全職 LCE 團隊。他們負責加速新產品和功能的發布，同時應用 SRE 的專業知識，確保 Google 交付的產品可靠、高可用且低延遲。

LCEs were responsible for making sure launches were executing quickly without the services falling over, and that if a launch did fail, it didn’t take down other products. LCEs were also responsible for keeping stakeholders informed of the nature and likelihood of such failures whenever corners were cut in order to accelerate time to market. Their consulting sessions were formalized as Production Reviews.
LCE 負責確保發布能夠快速執行，而不會導致服務崩潰，並且如果發布失敗，也不會拖垮其他產品。LCE 還負責在為了加快上市時間而偷工減料時，向利害關係人通報此類故障的性質和可能性。他們的諮詢會議被正式定為生產審查 (Production Reviews)。

## Evolution of the LCE Checklist
## LCE 檢查清單的演變

As Google’s environment grew more complex, so did both the Launch Coordination Engineering checklist (see Launch Coordination Checklist ) and the volume of launches. In 3.5 years, one LCE ran 350 launches through the LCE Checklist. As the team averaged five engineers during this time period, this translates into a Google launch throughput of over 1,500 launches in 3.5 years!
隨著 Google 環境變得更加複雜，發布協調工程 (Launch Coordination Engineering) 檢查清單（參見發布協調檢查清單）和發布量也隨之增加。在 3.5 年內，一位 LCE 透過 LCE 檢查清單執行了 350 次發布。由於在此期間團隊平均有五名工程師，這相當於 Google 在 3.5 年內有超過 1,500 次的發布吞吐量！

While each question on the LCE Checklist is simple, much complexity is built in to what prompted the question and the implications of its answer. In order to fully understand this degree of complexity, a new LCE hire requires about six months of training.
雖然 LCE 檢查清單上的每個問題都很簡單，但問題提出的動機及其答案的含義卻內建了許多複雜性。為了完全理解這種程度的複雜性，一位新進的 LCE 需要大約六個月的培訓。

As the volume of launches grew, keeping pace with the annual doubling of Google’s engineering team, LCEs sought ways to streamline their reviews. LCEs identified categories of low-risk launches that were highly unlikely to face or cause mishaps. For example, a feature launch involving no new server executables and a traffic increase under 10% would be deemed low risk. Such launches were faced with an almost trivial checklist, while higher-risk launches underwent the full gamut of checks and balances. By 2008, 30% of reviews were considered low-risk.
隨著發布量的增長，為了跟上 Google 工程團隊每年翻倍的步伐，LCE 尋求簡化審查的方法。LCE 確定了低風險發布的類別，這些發布極不可能面臨或引起意外。例如，一個不涉及新伺服器執行檔且流量增加低於 10% 的功能發布將被視為低風險。此類發布面臨的是一個幾乎微不足道的檢查清單，而較高風險的發布則需要經過全套的檢查與平衡。到 2008 年，30% 的審查被認為是低風險的。

Simultaneously, Google’s environment was scaling up, removing constraints on many launches. For instance, the acquisition of YouTube forced Google to build out its network and utilize bandwidth more efficiently. This meant that many smaller products would "fit within the cracks," avoiding complex network capacity planning and provisioning processes, thus accelerating their launches. Google also began building very large datacenters capable of hosting several dependent services under one roof. This development simplified the launch of new products that needed large amounts of capacity at multiple preexisting services upon which they depended.
與此同時，Google 的環境正在擴大規模，消除了許多發布的限制。例如，收購 YouTube 迫使 Google 擴建其網路並更有效地利用頻寬。這意味著許多較小的產品將「擠進夾縫中」，避免了複雜的網路容量規劃和配置流程，從而加速了它們的發布。Google 還開始建造能夠在同一屋簷下託管多個相依服務的超大型資料中心。這一發展簡化了新產品的發布，這些新產品需要在其所依賴的多個既有服務上獲得大量容量。

## Problems LCE Didn’t Solve
## LCE 未解決的問題

Although LCEs tried to keep the bureaucracy of reviews to a minimum, such efforts were insufficient. By 2009, the difficulties of launching a small new service at Google had become a legend. Services that grew to a larger scale faced their own set of problems that Launch Coordination could not solve.
雖然 LCE 試圖將審查的官僚作風降到最低，但這些努力還不夠。到 2009 年，在 Google 推出一個小型新服務的困難已經成為一個傳說。發展到更大規模的服務面臨著自己的一系列問題，而發布協調 (Launch Coordination) 無法解決這些問題。

### Scalability changes
### 可擴展性變更

When products are successful far beyond any early estimates, and their usage increases by more than two orders of magnitude, keeping pace with their load necessitates many design changes. Such scalability changes, combined with ongoing feature additions, often make the product more complex, fragile, and difficult to operate. At some point, the original product architecture becomes unmanageable and the product needs to be completely rearchitected. Rearchitecting the product and then migrating all users from the old to the new architecture requires a large investment of time and resources from developers and SREs alike, slowing down the rate of new feature development during that period.
當產品的成功遠遠超出任何早期估計，其使用量增加了兩個數量級以上時，要跟上其負載就需要進行許多設計變更。這種可擴展性的變更，再加上持續的功能增加，通常會使產品變得更複雜、脆弱且難以操作。在某個時候，原始的產品架構變得無法管理，產品需要被完全重新架構。重新架構產品，然後將所有使用者從舊架構遷移到新架構，需要開發人員和 SRE 投入大量的時間和資源，從而減緩了該時期新功能的開發速度。

### Growing operational load
### 不斷增長的營運負擔

When running a service after it launches, operational load, the amount of manual and repetitive engineering needed to keep a system functioning, tends to grow over time unless efforts are made to control such load. Noisiness of automated notifications, complexity of deployment procedures, and the overhead of manual maintenance work tend to increase over time and consume increasing amounts of the service owner’s bandwidth, leaving the team less time for feature development. SRE has an internally advertised goal of keeping operational work below a maximum of 50%; see Eliminating Toil . Staying below this maximum requires constant tracking of sources of operational work, as well as directed effort to remove these sources.
在服務推出後運行時，營運負擔——維持系統運作所需的手動和重複性工程量——除非努力控制，否則往往會隨著時間的推移而增長。自動化通知的嘈雜、部署程序的複雜性以及手動維護工作的開銷，往往會隨著時間的推移而增加，並消耗越來越多的服務所有者的頻寬，從而使團隊用於功能開發的時間減少。SRE 有一個內部宣傳的目標，即將營運工作保持在最高 50% 以下；請參閱「消除瑣務 (Eliminating Toil)」。要保持在該最大值以下，需要持續追蹤營運工作的來源，並有針對性地努力消除這些來源。

### Infrastructure churn
### 基礎設施流失

If the underlying infrastructure (such as systems for cluster management, storage, monitoring, load balancing, and data transfer) is changing due to active development by infrastructure teams, the owners of services running on the infrastructure must invest large amounts of work to simply keep up with the infrastructure changes. As infrastructure features upon which services rely are deprecated and replaced by new features, service owners must continually modify their configurations and rebuild their executables, consequently "running fast just to stay in the same place." The solution to this scenario is to enact some type of churn reduction policy that prohibits infrastructure engineers from releasing backward-incompatible features until they also automate the migration of their clients to the new feature. Creating automated migration tools to accompany new features minimizes the work imposed on service owners to keep up with infrastructure churn.
如果底層基礎設施（例如叢集管理、儲存、監控、負載平衡和資料傳輸系統）因基礎設施團隊的積極開發而發生變化，那麼運行在該基礎設施上的服務的所有者必須投入大量工作，才能跟上基礎設施的變化。隨著服務所依賴的基礎設施功能被棄用並被新功能取代，服務所有者必須不斷修改其設定並重建其可執行檔，從而「快速奔跑只為停在原地」。這種情況的解決方案是制定某種類型的流失減少政策，禁止基礎設施工程師發布向後不相容的功能，除非他們也自動將其客戶端遷移到新功能。建立自動遷移工具以配合新功能，可以最大限度地減少服務所有者為跟上基礎設施流失而付出的工作。

Solving these problems requires company-wide efforts that are far beyond the scope of LCE: a combination of better platform APIs and frameworks (see The Evolving SRE Engagement Model ), continuous build and test automation, and better standardization and automation across Google’s production services.
解決這些問題需要全公司範圍的努力，遠遠超出了 LCE 的範圍：需要結合更好的平台 API 和框架（參見「不斷演進的 SRE 參與模型」）、持續的建置和測試自動化，以及 Google 生產服務中更好的標準化和自動化。

# Conclusion
# 結論

Companies undergoing rapid growth with a high rate of change to products and services may benefit from the equivalent of a Launch Coordination Engineering role. Such a team is especially valuable if a company plans to double its product developers every one or two years, if it must scale its services to hundreds of millions of users, and if reliability despite a high rate of change is important to its users.
經歷快速增長且產品和服務變化率高的公司，可能會從相當於發布協調工程 (Launch Coordination Engineering) 角色的職位中受益。如果一家公司計劃每一到兩年將其產品開發人員數量翻倍，如果它必須將其服務擴展到數億使用者，並且如果儘管變化率高但可靠性對其使用者很重要，那麼這樣一個團隊尤其有價值。

The LCE team was Google’s solution to the problem of achieving safety without impeding change. This chapter introduced some of the experiences accumulated by our unique LCE role over a 10-year period under exactly such circumstances. We hope that our approach will help inspire others facing similar challenges in their respective organizations.
LCE 團隊是 Google 解決在不阻礙變革的情況下實現安全問題的方案。本章介紹了我們獨特的 LCE 角色在整整 10 年的時間裡，在這樣的情況下所累積的一些經驗。我們希望我們的方法能激勵其他在各自組織中面臨類似挑戰的人。
