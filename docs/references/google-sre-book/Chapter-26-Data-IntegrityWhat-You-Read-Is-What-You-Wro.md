## Data Integrity: What You Read Is What You Wrote
## 資料完整性：所讀即所寫

Written by Raymond Blum and Rhandeev Singh Edited by Betsy Beyer
作者：Raymond Blum 和 Rhandeev Singh，編輯：Betsy Beyer

What is "data integrity"? When users come first, data integrity is whatever users think it is.
什麼是「資料完整性」？當使用者至上時，資料完整性就是使用者認為的那個樣子。

We might say data integrity is a measure of the accessibility and accuracy of the datastores needed to provide users with an adequate level of service . But this definition is insufficient.
我們或許會說，資料完整性是衡量為使用者提供足夠服務水準所需的資料儲存庫的可存取性和準確性的指標。但這個定義並不充分。

For instance, if a user interface bug in Gmail displays an empty mailbox for too long, users might believe data has been lost. Thus, even if no data was actually lost, the world would question Google’s ability to act as a responsible steward of data, and the viability of cloud computing would be threatened. Were Gmail to display an error or maintenance message for too long while "only a bit of metadata" is repaired, the trust of Google’s users would similarly erode.
例如，如果 Gmail 的一個使用者介面錯誤導致信箱長時間顯示為空，使用者可能會認為資料已經遺失。因此，即使實際上沒有資料遺失，世界也會質疑 Google 作為資料負責任保管者的能力，雲端運算 (cloud computing) 的生存能力也會受到威脅。如果 Gmail 在修復「僅僅是一點元資料 (metadata)」的過程中長時間顯示錯誤或維護訊息，Google 使用者的信任同樣會受到侵蝕。

How long is "too long" for data to be unavailable? As demonstrated by an actual Gmail incident in 2011 [Hic11] , four days is a long time perhaps "too long." Subsequently, we believe 24 hours is a good starting point for establishing the threshold of "too long" for Google Apps.
資料無法使用的「太長」時間是多久？正如 2011 年一次真實的 Gmail 事件 [Hic11] 所示，四天是一段很長的時間——或許是「太長」了。後來，我們認為 24 小時是為 Google Apps 設定「太長」閾值的一個良好起點。

Similar reasoning applies to applications like Google Photos, Drive, Cloud Storage, and Cloud Datastore, because users don’t necessarily draw a distinction between these discrete products (reasoning, "this product is still Google" or "Google, Amazon, whatever; this product is still part of the cloud"). Data loss, data corruption, and extended unavailability are typically indistinguishable to users. Therefore, data integrity applies to all types of data across all services. When considering data integrity, what matters is that services in the cloud remain accessible to users. User access to data is especially important .
類似的道理也適用於 Google 相簿 (Google Photos)、雲端硬碟 (Drive)、雲端儲存 (Cloud Storage) 和雲端資料儲存 (Cloud Datastore) 等應用程式，因為使用者不一定會區分這些獨立的產品（他們會想，「這個產品仍然是 Google 的」或「Google、Amazon，都一樣；這個產品仍然是雲端的一部分」）。資料遺失、資料損毀和長時間的不可用性對使用者來說通常是無法區分的。因此，資料完整性適用於所有服務中的所有類型的資料。在考慮資料完整性時，重要的是雲端中的服務對使用者保持可存取。使用者對資料的存取尤其重要。

# Data Integrity’s Strict Requirements
# 資料完整性的嚴格要求

When considering the reliability needs of a given system, it may seem that uptime (service availability) needs are stricter than those of data integrity. For example, users may find an hour of email downtime unacceptable, whereas they may live grumpily with a four-day time window to recover a mailbox. However, there’s a more appropriate way to consider the demands of uptime versus data integrity.
在考慮一個特定系統的可靠性需求時，似乎正常執行時間（服務可用性）的需求比資料完整性的需求更為嚴格。例如，使用者可能會覺得一小時的電子郵件停機是不可接受的，而他們可能會不悅地忍受四天的時間來恢復一個信箱。然而，有一種更恰當的方式來考量正常執行時間與資料完整性之間的需求。

An SLO of 99.99% uptime leaves room for only an hour of downtime in a whole year. This SLO sets a rather high bar, which likely exceeds the expectations of most Internet and Enterprise users.
一個 99.99% 正常執行時間的服務等級目標 (SLO) 一整年只允許一小時的停機時間。這個 SLO 設定了一個相當高的標準，很可能超出了大多數網際網路和企業使用者的期望。

In contrast, an SLO of 99.99% good bytes in a 2 GB artifact would render documents, executables, and databases corrupt (up to 200 KB garbled). This amount of corruption is catastrophic in the majority of cases resulting in executables with random opcodes and completely unloadable databases.
相比之下，在一個 2 GB 的檔案中，99.99% 的良好位元組的 SLO 會導致文件、執行檔和資料庫損毀（最多 200 KB 的亂碼）。在大多數情況下，這種程度的損毀是災難性的，會導致執行檔出現隨機的操作碼和完全無法載入的資料庫。

From the user perspective, then, every service has independent uptime and data integrity requirements, even if these requirements are implicit. The worst time to disagree with users about these requirements is after the demise of their data!
那麼，從使用者的角度來看，每個服務都有獨立的正常執行時間和資料完整性要求，即使這些要求是隱含的。與使用者就這些要求產生分歧最糟糕的時機，是在他們的資料消失之後！

To revise our earlier definition of data integrity, we might say that data integrity means that services in the cloud remain accessible to users. User access to data is especially important, so this access should remain in perfect shape .
為了修正我們早先對資料完整性的定義，我們或許可以說，資料完整性意味著雲端中的服務對使用者保持可存取。使用者對資料的存取尤其重要，所以這種存取應該保持在完美的狀態。

Now, suppose an artifact were corrupted or lost exactly once a year. If the loss were unrecoverable, uptime of the affected artifact is lost for that year. The most likely means to avoid any such loss is through proactive detection, coupled with rapid repair.
現在，假設一個檔案每年恰好損毀或遺失一次。如果損失是無法恢復的，那麼受影響檔案的該年度正常執行時間就喪失了。避免任何此類損失最可能的方法是透過主動偵測，並結合快速修復。

In an alternate universe, suppose the corruption were immediately detected before users were affected and that the artifact was removed, fixed, and returned to service within half an hour. Ignoring any other downtime during that 30 minutes, such an object would be 99.99% available that year.
在另一個平行時空，假設在影響使用者之前就立即偵測到損毀，並且該檔案在半小時內被移除、修復並恢復服務。忽略那 30 分鐘內的任何其他停機時間，這樣一個物件在那一年的可用性將達到 99.99%。

Astonishingly, at least from the user perspective, in this scenario, data integrity is still 100% (or close to 100%) during the accessible lifetime of the object. As demonstrated by this example, the secret to superior data integrity is proactive detection and rapid repair and recovery.
令人驚訝的是，至少從使用者的角度來看，在這種情況下，資料完整性在該物件的可存取生命週期內仍然是 100%（或接近 100%）。正如這個例子所示，實現卓越資料完整性的秘訣在於主動偵測以及快速的修復和恢復。

## Choosing a Strategy for Superior Data Integrity
## 選擇卓越資料完整性的策略

There are many possible strategies for rapid detection, repair, and recovery of lost data. All of these strategies trade uptime against data integrity with respect to affected users. Some strategies work better than others, and some strategies require more complex engineering investment than others. With so many options available, which strategies should you utilize? The answer depends on your computing paradigm.
對於遺失資料的快速偵測、修復和恢復，有許多可能的策略。所有這些策略都在受影響使用者的正常執行時間與資料完整性之間進行權衡。有些策略比其他策略效果更好，有些策略則需要更複雜的工程投資。有這麼多選擇，你應該使用哪些策略呢？答案取決於你的運算模式。

Most cloud computing applications seek to optimize for some combination of uptime, latency, scale, velocity, and privacy. To provide a working definition for each of these terms:
大多數雲端運算應用程式都試圖在正常執行時間、延遲、規模、速度和隱私之間尋求某種組合的最佳化。以下為每個術語提供一個可操作的定義：

Many cloud applications continually evolve atop a mixture of ACID 122 and BASE 123 APIs to meet the demands of these five components. 124 BASE allows for higher availability than ACID, in exchange for a softer distributed consistency guarantee. Specifically, BASE only guarantees that once a piece of data is no longer updated, its value will eventually become consistent across (potentially distributed) storage locations.
許多雲端應用程式在混合了 ACID 122 和 BASE 123 API 的基礎上不斷發展，以滿足這五個元件的需求。124 BASE 允許比 ACID 更高的可用性，以換取較軟的分散式一致性保證。具體來說，BASE 只保證一旦一筆資料不再更新，其值最終將在（可能分散的）儲存位置之間變得一致。

The following scenario provides an example of how trade-offs between uptime, latency, scale, velocity, and privacy might play out.
以下情境提供了一個範例，說明正常執行時間、延遲、規模、速度和隱私之間的權衡如何發揮作用。

When velocity trumps other requirements, the resulting applications rely on an arbitrary collection of APIs that are most familiar to the particular developers working on the application.
當速度勝過其他要求時，由此產生的應用程式會依賴於特定開發人員最熟悉的一組任意 API。

For example, an application may take advantage of an efficient BLOB 125 storage API, such as Blobstore, that neglects distributed consistency in favor of scaling to heavy workloads with high uptime, low latency, and at low cost. To compensate:
例如，一個應用程式可能會利用高效的 BLOB 125 儲存 API，例如 Blobstore，它忽略了分散式一致性，以支援擴展到高正常執行時間、低延遲和低成本的繁重工作負載。為了彌補：

The same application may entrust small amounts of authoritative metadata pertaining to its blobs to a higher latency, less available, more costly Paxos-based service such as Megastore [Bak11] , [Lam98] . Certain clients of the application may cache some of that metadata locally and access blobs directly, shaving latency still further from the vantage point of users. Another application may keep metadata in Bigtable, sacrificing strong distributed consistency because its developers happened to be familiar with Bigtable.
同一個應用程式可能會將與其 blob 相關的少量權威性元資料託付給一個延遲更高、可用性更低、成本更高的基於 Paxos 的服務，例如 Megastore [Bak11] , [Lam98]。該應用程式的某些客戶端可能會在本地快取其中一些元資料，並直接存取 blob，從而從使用者的角度進一步縮短延遲。另一個應用程式可能會將元資料保存在 Bigtable 中，犧牲強分散式一致性，因為其開發人員恰好熟悉 Bigtable。

- The same application may entrust small amounts of authoritative metadata pertaining to its blobs to a higher latency, less available, more costly Paxos-based service such as Megastore [Bak11] , [Lam98] .
- 同一個應用程式可能會將與其 blob 相關的少量權威性元資料託付給一個延遲更高、可用性更低、成本更高的基於 Paxos 的服務，例如 Megastore [Bak11] , [Lam98]。

- Certain clients of the application may cache some of that metadata locally and access blobs directly, shaving latency still further from the vantage point of users.
- 該應用程式的某些客戶端可能會在本地快取其中一些元資料，並直接存取 blob，從而從使用者的角度進一步縮短延遲。

- Another application may keep metadata in Bigtable, sacrificing strong distributed consistency because its developers happened to be familiar with Bigtable.
- 另一個應用程式可能會將元資料保存在 Bigtable 中，犧牲強分散式一致性，因為其開發人員恰好熟悉 Bigtable。

Such cloud applications face a variety of data integrity challenges at runtime, such as referential integrity between datastores (in the preceding example, Blobstore, Megastore, and client-side caches). The vagaries of high velocity dictate that schema changes, data migrations, the piling of new features atop old features, rewrites, and evolving integration points with other applications collude to produce an environment riddled with complex relationships between various pieces of data that no single engineer fully groks.
這樣的雲端應用程式在執行時面臨各種資料完整性挑戰，例如資料儲存庫之間的參考完整性（在前面的例子中，是 Blobstore、Megastore 和客戶端快取）。高速度的變幻莫測意味著結構描述變更、資料遷移、在新功能之上堆疊新功能、重寫以及與其他應用程式不斷發展的整合點，共同造成了一個充滿複雜資料關係的環境，沒有任何一個工程師能完全理解。

To prevent such an application’s data from degrading before its users’ eyes, a system of out-of-band checks and balances is needed within and between its datastores. Third Layer: Early Detection discusses such a system.
為了防止這類應用程式的資料在使用者眼前退化，需要在其資料儲存庫內部和之間建立一個帶外 (out-of-band) 的檢查與平衡系統。第三層：早期偵測討論了這樣一個系統。

In addition, if such an application relies on independent, uncoordinated backups of several datastores (in the preceding example, Blobstore and Megastore), then its ability to make effective use of restored data during a data recovery effort is complicated by the variety of relationships between restored and live data. Our example application would have to sort through and distinguish between restored blobs versus live Megastore, restored Megastore versus live blobs, restored blobs versus restored Megastore, and interactions with client-side caches.
此外，如果此類應用程式依賴於多個資料儲存庫（在前面的例子中是 Blobstore 和 Megastore）的獨立、未協調的備份，那麼在資料恢復工作中有效利用已恢復資料的能力，會因為已恢復資料和即時資料之間的各種關係而變得複雜。我們的範例應用程式將必須整理和區分：恢復的 blob 與即時的 Megastore、恢復的 Megastore 與即時的 blob、恢復的 blob 與恢復的 Megastore，以及與客戶端快取的互動。

In consideration of these dependencies and complications, how many resources should be invested in data integrity efforts, and where?
考慮到這些依賴性和複雜性，應該在資料完整性工作上投入多少資源，又該投在哪裡？

## Backups Versus Archives
## 備份與封存

Traditionally, companies "protect" data against loss by investing in backup strategies. However, the real focus of such backup efforts should be data recovery, which distinguishes real backups from archives. As is sometimes observed: No one really wants to make backups; what people really want are restores .
傳統上，公司透過投資備份策略來「保護」資料免於遺失。然而，這類備份工作的真正重點應該是資料恢復，這也是真正備份與封存的區別所在。正如人們有時所說：沒有人真的想做備份；人們真正想要的是恢復 (restore)。

Is your "backup" really an archive, rather than appropriate for use in disaster recovery ?
你的「備份」真的是一個封存，而不是適用於災難恢復嗎？

The most important difference between backups and archives is that backups can be loaded back into an application, while archives cannot . Therefore, backups and archives have quite differing use cases.
備份和封存之間最重要的區別是，備份可以被載入回應用程式中，而封存則不能。因此，備份和封存有著截然不同的使用案例。

Archives safekeep data for long periods of time to meet auditing, discovery, and compliance needs. Data recovery for such purposes generally doesn’t need to complete within uptime requirements of a service. For example, you might need to retain financial transaction data for seven years. To achieve this goal, you could move accumulated audit logs to long-term archival storage at an offsite location once a month. Retrieving and recovering the logs during a month-long financial audit may take a week, and this weeklong time window for recovery may be acceptable for an archive.
封存 (Archives) 長期保管資料以滿足稽核、法律調查和合規性需求。為此目的的資料恢復通常不需要在服務的正常執行時間要求內完成。例如，你可能需要將金融交易資料保留七年。為了達到這個目標，你可以每月將累積的稽核日誌移至異地的長期封存儲存中。在為期一個月的財務稽核期間，檢索和恢復日誌可能需要一週的時間，而這一週的恢復時間對於封存來說可能是可以接受的。

On the other hand, when disaster strikes, data must be recovered from real backups quickly, preferably well within the uptime needs of a service. Otherwise, affected users are left without useful access to the application from the onset of the data integrity issue until the completion of the recovery effort.
另一方面，當災難來臨時，資料必須從真正的備份中快速恢復，最好是在服務的正常執行時間需求之內。否則，受影響的使用者從資料完整性問題發生開始，直到恢復工作完成，都將無法有效存取應用程式。

It’s also important to consider that because the most recent data is at risk until safely backed up, it may be optimal to schedule real backups (as opposed to archives) to occur daily, hourly, or more frequently, using full and incremental or continuous (streaming) approaches.
同樣重要的是要考慮到，由於最新的資料在安全備份之前一直處於風險之中，因此最好安排真正的備份（而不是封存）每天、每小時或更頻繁地進行，使用完整備份、增量備份或連續（串流）備份的方法。

Therefore, when formulating a backup strategy, consider how quickly you need to be able to recover from a problem, and how much recent data you can afford to lose.
因此，在制定備份策略時，請考慮你需要多快從問題中恢復，以及你能夠承受多少近期資料的損失。

## Requirements of the Cloud Environment in Perspective
## 從雲端環境的角度看需求

Cloud environments introduce a unique combination of technical challenges:
雲端環境帶來了一系列獨特的技術挑戰：

If the environment uses a mixture of transactional and nontransactional backup and restore solutions, recovered data won’t necessarily be correct. If services must evolve without going down for maintenance, different versions of business logic may act on data in parallel. If interacting services are versioned independently, incompatible versions of different services may interact momentarily, further increasing the chance of accidental data corruption or data loss.
如果環境使用混合的交易式和非交易式備份與還原解決方案，恢復的資料不一定正確。如果服務必須在不停機維護的情況下演進，不同版本的業務邏輯可能會並行處理資料。如果互動的服務是獨立版本化的，不相容版本的不同服務可能會短暫互動，進一步增加了意外資料損毀或遺失的機會。

- If the environment uses a mixture of transactional and nontransactional backup and restore solutions, recovered data won’t necessarily be correct.
- 如果環境使用混合的交易式和非交易式備份與還原解決方案，恢復的資料不一定正確。

- If services must evolve without going down for maintenance, different versions of business logic may act on data in parallel.
- 如果服務必須在不停機維護的情況下演進，不同版本的業務邏輯可能會並行處理資料。

- If interacting services are versioned independently, incompatible versions of different services may interact momentarily, further increasing the chance of accidental data corruption or data loss.
- 如果互動的服務是獨立版本化的，不相容版本的不同服務可能會短暫互動，進一步增加了意外資料損毀或遺失的機會。

In addition, in order to maintain economy of scale, service providers must provide only a limited number of APIs. These APIs must be simple and easy to use for the vast majority of applications, or few customers will use them. At the same time, the APIs must be robust enough to understand the following:
此外，為了維持規模經濟，服務提供者必須只提供有限數量的 API。這些 API 必須對絕大多數應用程式來說簡單易用，否則很少有客戶會使用它們。同時，這些 API 必須足夠強大，以理解以下內容：

Data locality and caching Local and global data distribution Strong and/or eventual consistency Data durability, backup, and recovery
資料本地性與快取、本地與全域資料分佈、強一致性與/或最終一致性、資料持久性、備份與恢復。

- Data locality and caching
- 資料本地性與快取

- Local and global data distribution
- 本地與全域資料分佈

- Strong and/or eventual consistency
- 強一致性與/或最終一致性

- Data durability, backup, and recovery
- 資料持久性、備份與恢復

Otherwise, sophisticated customers can’t migrate applications to the cloud, and simple applications that grow complex and large will need complete rewrites in order to use different, more complex APIs.
否則，複雜的客戶無法將應用程式遷移到雲端，而那些變得複雜和龐大的簡單應用程式將需要完全重寫，才能使用不同的、更複雜的 API。

Problems arise when the preceding API features are used in certain combinations. If the service provider doesn’t solve these problems, then the applications that run into these challenges must identify and solve them independently.
當上述 API 功能以某些組合使用時，問題就會出現。如果服務提供者不解決這些問題，那麼遇到這些挑戰的應用程式必須獨立地識別和解決它們。

# Google SRE Objectives in Maintaining Data Integrity and Availability
# Google SRE 在維護資料完整性與可用性方面的目標

While SRE’s goal of “maintaining integrity of persistent data” is a good vision, we thrive on concrete objectives with measurable indicators. SRE defines key metrics that we use to set expectations for the capabilities of our systems and processes through tests and to track their performance during an actual event.
雖然 SRE「維護持久性資料完整性」的目標是一個很好的願景，但我們更專注於具有可衡量指標的具體目標。SRE 定義了關鍵指標，我們用這些指標透過測試來設定對我們系統和流程能力的期望，並在實際事件中追蹤其表現。

## Data Integrity Is the Means; Data Availability Is the Goal
## 資料完整性是手段；資料可用性是目標

Data integrity refers to the accuracy and consistency of data throughout its lifetime. Users need to know that information will be correct and won’t change in some unexpected way from the time it’s first recorded to the last time it’s observed. But is such assurance enough?
資料完整性指的是資料在其整個生命週期中的準確性和一致性。使用者需要知道，從資訊首次被記錄到最後一次被觀察，它都將是正確的，並且不會以任何意想不到的方式發生變化。但這樣的保證足夠嗎？

Consider the case of an email provider who suffered a weeklong data outage [Kinc09] . Over the space of 10 days, users had to find other, temporary methods of conducting their business with the expectation that they’d soon return to their established email accounts, identities, and accumulated histories.
考慮一個電子郵件提供商的案例，他們遭遇了長達一週的資料中斷 [Kinc09]。在 10 天的時間裡，使用者不得不尋找其他臨時的方法來處理他們的業務，並期望他們能很快回到他們已建立的電子郵件帳戶、身份和累積的歷史記錄中。

Then, the worst possible news arrived: the provider announced that despite earlier expectations, the trove of past email and contacts was in fact gone evaporated and never to be seen again. It seemed that a series of mishaps in managing data integrity had conspired to leave the service provider with no usable backups. Furious users either stuck with their interim identities or established new identities, abandoning their troubled former email provider.
然後，最壞的消息傳來了：供應商宣布，儘管早先有所期待，但過去的電子郵件和聯絡人寶庫實際上已經消失——蒸發了，再也看不到了。似乎是一系列在管理資料完整性方面的失誤，共同導致了該服務提供商沒有可用的備份。憤怒的使用者要麼繼續使用他們的臨時身份，要麼建立新的身份，拋棄了他們陷入困境的前電子郵件提供商。

But wait! Several days after the declaration of absolute loss, the provider announced that the users’ personal information could be recovered. There was no data loss; this was only an outage. All was well!
但是等等！在宣布完全遺失幾天後，供應商宣布使用者的個人資訊可以被恢復。沒有資料遺失；這只是一次中斷。一切都好了！

Except, all was not well . User data had been preserved, but the data was not accessible by the people who needed it for too long.
除了，並非一切都好。使用者資料被保存了下來，但需要它的人在太長的時間內無法存取這些資料。

The moral of this example: From the user’s point of view, data integrity without expected and regular data availability is effectively the same as having no data at all.
這個例子的寓意是：從使用者的角度來看，沒有預期和常規資料可用性的資料完整性，實際上就等於根本沒有資料。

## Delivering a Recovery System, Rather Than a Backup System
## 提供一個恢復系統，而非備份系統

Making backups is a classically neglected, delegated, and deferred task of system administration. Backups aren’t a high priority for anyone they’re an ongoing drain on time and resources, and yield no immediate visible benefit. For this reason, a lack of diligence in implementing a backup strategy is typically met with a sympathetic eye roll. One might argue that, like most measures of protection against low-risk dangers, such an attitude is pragmatic. The fundamental problem with this lackadaisical strategy is that the dangers it entails may be low risk, but they are also high impact. When your service’s data is unavailable, your response can make or break your service, product, and even your company.
製作備份是系統管理中一個典型被忽視、委派和延遲的任務。備份對任何人來說都不是高度優先事項——它們持續消耗時間和資源，卻沒有立即的明顯好處。因此，在實施備份策略時缺乏勤勉，通常只會得到同情的白眼。有人可能會爭辯說，就像大多數針對低風險危險的保護措施一樣，這種態度是務實的。這種懶散策略的根本問題在於，它所帶來的危險可能是低風險的，但也是高衝擊的。當你的服務資料不可用時，你的應對措施可以決定你的服務、產品，甚至你的公司的成敗。

Instead of focusing on the thankless job of taking a backup, it’s much more useful, not to mention easier, to motivate participation in taking backups by concentrating on a task with a visible payoff: the restore ! Backups are a tax , one paid on an ongoing basis for the municipal service of guaranteed data availability. Instead of emphasizing the tax, draw attention to the service the tax funds: data availability. We don’t make teams "practice" their backups, instead:
與其專注於吃力不討好的備份工作，不如專注於一個有明顯回報的任務來激勵大家參與備份：恢復 (restore)！這會更有用，也更容易。備份是一種稅，是為保證資料可用性這項市政服務而持續支付的。與其強調稅收，不如將注意力吸引到稅收所資助的服務上：資料可用性。我們不讓團隊「練習」他們的備份，而是：

Teams define service level objectives (SLOs) for data availability
        in a variety of failure modes. A team practices and demonstrates their ability to meet those SLOs.
團隊為各種故障模式下的資料可用性定義服務等級目標 (SLO)。一個團隊練習並展示他們滿足這些 SLO 的能力。

- Teams define service level objectives (SLOs) for data availability in a variety of failure modes.
- 團隊為各種故障模式下的資料可用性定義服務等級目標 (SLO)。

- A team practices and demonstrates their ability to meet those SLOs.
- 一個團隊練習並展示他們滿足這些 SLO 的能力。

## Types of Failures That Lead to Data Loss
## 導致資料遺失的故障類型

As illustrated by Figure 26-3 , at a very high level, there are 24 distinct types of failures when the 3 factors can occur in any combination. You should consider each of these potential failures when designing a data integrity program. The factors of data integrity failure modes are as follows:
如圖 26-3 所示，在一個非常高的層級上，當 3 個因素可以任意組合發生時，存在 24 種不同的故障類型。在設計資料完整性計畫時，你應該考慮所有這些潛在的故障。資料完整性故障模式的因素如下：

An effective restore plan must account for any of these failure modes occurring in any conceivable combination. What may be a perfectly effective strategy for guarding against a data loss caused by a creeping application bug may be of no help whatsoever when your colocation datacenter catches fire.
一個有效的恢復計畫必須考慮到任何這些故障模式以任何可想見的組合發生。一個對於防範由潛伏的應用程式錯誤引起的資料遺失可能非常有效的策略，在你的主機託管資料中心發生火災時可能完全沒有幫助。

A study of 19 data recovery efforts at Google found that the most common user-visible data loss scenarios involved data deletion or loss of referential integrity caused by software bugs. The most challenging variants involved low-grade corruption or deletion that was discovered weeks to months after the bugs were first released into the production environment. Therefore, the safeguards Google employs should be well suited to prevent or recover from these types of loss.
一項針對 Google 19 次資料恢復工作的研究發現，最常見的使用者可見的資料遺失情境涉及由軟體錯誤引起的資料刪除或參考完整性喪失。最具挑戰性的變體涉及低度損毀或刪除，這些問題是在錯誤首次發布到生產環境數週到數月後才被發現。因此，Google 採用的保護措施應該非常適合預防或從這些類型的損失中恢復。

To recover from such scenarios, a large and successful application needs to retrieve data for perhaps millions of users spread across days, weeks, or months. The application may also need to recover each affected artifact to a unique point in time. This data recovery scenario is called "point-in-time recovery" outside Google, and "time-travel" inside Google.
為了從這種情況中恢復，一個大型且成功的應用程式需要為可能數百萬的使用者檢索分佈在數天、數週或數月內的資料。該應用程式可能還需要將每個受影響的檔案恢復到一個獨特的時間點。這種資料恢復情境在 Google 外部被稱為「時間點恢復 (point-in-time recovery)」，在 Google 內部則被稱為「時間旅行 (time-travel)」。

A backup and recovery solution that provides point-in-time recovery for an application across its ACID and BASE datastores while meeting strict uptime, latency, scalability, velocity, and cost goals is a chimera today!
一個能夠為應用程式在其 ACID 和 BASE 資料儲存庫上提供時間點恢復，同時滿足嚴格的正常執行時間、延遲、可擴展性、速度和成本目標的備份和恢復解決方案，在今天仍然是一個幻想！

Solving this problem with your own engineers entails sacrificing velocity. Many projects compromise by adopting a tiered backup strategy without point-in-time recovery. For instance, the APIs beneath your application may support a variety of data recovery mechanisms. Expensive local "snapshots" may provide limited protection from application bugs and offer quick restoration functionality, so you might retain a few days of such local "snapshots," taken several hours apart. Cost-effective full and incremental copies every two days may be retained longer. Point-in-time recovery is a very nice feature to have if one or more of these strategies support it.
用你自己的工程師解決這個問題意味著犧牲速度。許多專案透過採用沒有時間點恢復 (point-in-time recovery) 的分層備份策略來妥協。例如，你應用程式底層的 API 可能支援多種資料恢復機制。昂貴的本地「快照 (snapshots)」可以提供對應用程式錯誤的有限保護，並提供快速的還原功能，所以你可能會保留幾天這樣的本地「快照」，每隔幾小時拍攝一次。成本效益高的完整和增量副本每兩天一次，可以保留更長時間。如果這些策略中有一種或多種支援時間點恢復，那將是一個非常好的功能。

Consider the data recovery options provided by the cloud APIs you are about to use. Trade point-in-time recovery against a tiered strategy if necessary, but don’t resort to not using either! If you can have both features, use both features. Each of these features (or both) will be valuable at some point.
考慮你將要使用的雲端 API 提供的資料恢復選項。如有必要，在時間點恢復 (point-in-time recovery) 和分層策略之間進行權衡，但不要兩者都不用！如果你可以同時擁有這兩個功能，就都使用。這些功能中的每一個（或兩者）在某些時候都會很有價值。

## Challenges of Maintaining Data Integrity Deep and Wide
## 維護深度與廣度資料完整性的挑戰

In designing a data integrity program, it’s important to recognize that replication and redundancy are not recoverability .
在設計資料完整性計畫時，重要的是要認識到複製 (replication) 和冗餘 (redundancy) 並不等於可恢復性 (recoverability)。

### Scaling issues: Fulls, incrementals, and the competing forces of backups and restores
### 擴展問題：完整備份、增量備份以及備份與還原的競爭力量

A classic but flawed response to the question "Do you have a backup?" is "We have something even better than a backup replication!" Replication provides many benefits, including locality of data and protection from a site-specific disaster, but it can’t protect you from many sources of data loss. Datastores that automatically sync multiple replicas guarantee that a corrupt database row or errant delete are pushed to all of your copies, likely before you can isolate the problem.
對於「你有備份嗎？」這個問題，一個經典但有缺陷的回答是：「我們有比備份更好的東西——複製 (replication)！」複製提供了許多好處，包括資料的本地性和免於站點特定災難的保護，但它無法保護你免於許多資料遺失的來源。自動同步多個複本的資料儲存庫保證了損壞的資料庫行或錯誤的刪除會被推送到你所有的複本中，很可能在你能夠隔離問題之前就發生了。

To address this concern, you might make nonserving copies of your data in some other format, such as frequent database exports to a native file. This additional measure adds protection from the types of errors replication doesn’t protect against user errors and application-layer bugs but does nothing to guard against losses introduced at a lower layer. This measure also introduces a risk of bugs during data conversion (in both directions) and during storage of the native file, in addition to possible mismatches in semantics between the two formats. Imagine a zero-day attack 126 at some low level of your stack, such as the filesystem or device driver. Any copies that rely on the compromised software component, including the database exports that were written to the same filesystem that backs your database, are vulnerable .
為了處理這個問題，你可能會以其他格式製作非服務用的資料副本，例如頻繁地將資料庫匯出為原生檔案。這個額外的措施增加了對複製 (replication) 無法防範的錯誤類型（使用者錯誤和應用程式層級的錯誤）的保護，但對於在更低層級引入的損失則無能為力。這個措施也引入了在資料轉換（雙向）和原生檔案儲存期間出現錯誤的風險，此外還可能存在兩種格式之間語義不匹配的問題。想像一下，在你的技術堆疊的某個低層級，例如檔案系統或裝置驅動程式，發生了零時差攻擊 (zero-day attack) 126。任何依賴於受損軟體元件的副本，包括寫入到支援你資料庫的相同檔案系統的資料庫匯出檔案，都是脆弱的。

Thus, we see that diversity is key: protecting against a failure at layer X requires storing data on diverse components at that layer. Media isolation protects against media flaws: a bug or attack in a disk device driver is unlikely to affect tape drives. If we could, we’d make backup copies of our valuable data on clay tablets. 127
因此，我們看到多樣性是關鍵：為了防範在第 X 層的故障，需要在該層使用多樣化的元件來儲存資料。媒體隔離可以防範媒體缺陷：磁碟裝置驅動程式中的錯誤或攻擊不太可能影響磁帶機。如果可以的話，我們會用泥板來備份我們寶貴的資料。127

The forces of data freshness and restore completion compete against comprehensive protection. The further down the stack you push a snapshot of your data, the longer it takes to make a copy, which means that the frequency of copies decreases. At the database level, a transaction may take on the order of seconds to replicate. Exporting a database snapshot to the filesystem underneath may take 40 minutes. A full backup of the underlying filesystem may take hours.
資料新鮮度和恢復完成度這兩種力量與全面保護相互競爭。你將資料快照推到技術堆疊的越底層，製作副本所需的時間就越長，這意味著副本的頻率會降低。在資料庫層級，一個交易可能需要幾秒鐘來複製。將資料庫快照匯出到底層檔案系統可能需要 40 分鐘。對底層檔案系統進行完整備份可能需要數小時。

In this scenario, you may lose up to 40 minutes of the most recent data when you restore the latest snapshot. A restore from the filesystem backup might incur hours of missing transactions. Additionally, restoring probably takes as long as backing up, so actually loading the data might take hours. You’d obviously like to have the freshest data back as quickly as possible, but depending on the type of failure, that freshest and most immediately available copy might not be an option.
在這種情況下，當你還原最新的快照時，你可能會遺失長達 40 分鐘的最新資料。從檔案系統備份還原可能會導致數小時的交易遺失。此外，還原所需的時間可能和備份一樣長，所以實際載入資料可能需要數小時。你顯然希望盡快取回最新的資料，但根據故障的類型，最新且最容易取得的副本可能不是一個選項。

### Retention
### 保留

Retention how long you keep copies of your data around is yet another factor to consider in your data recovery plans.
保留期——你將資料副本保留多久——是你在資料恢復計畫中需要考慮的另一個因素。

While it’s likely that you or your customers will quickly notice the sudden emptying of an entire database, it might take days for a more gradual loss of data to attract the right person’s attention. Restoring the lost data in the latter scenario requires snapshots taken further back in time. When reaching back this far, you’ll likely want to merge the restored data with the current state. Doing so significantly complicates the restore process.
雖然你或你的客戶很可能會很快注意到整個資料庫突然被清空，但更漸進的資料遺失可能需要數天才能引起相關人員的注意。在後一種情況下恢復遺失的資料，需要使用更早時間點的快照。當回溯到這麼久遠的時候，你很可能會希望將恢復的資料與當前狀態合併。這樣做會使恢復過程變得非常複雜。

# How Google SRE Faces the Challenges of Data Integrity
# Google SRE 如何應對資料完整性的挑戰

Similar to our assumption that Google’s underlying systems are prone to failure, we assume that any of our protection mechanisms are also subject to the same forces and can fail in the same ways and at the most inconvenient of times. Maintaining a guarantee of data integrity at large scale, a challenge that is further complicated by the high rate of change of the involved software systems, requires a number of complementary but uncoupled practices, each chosen to offer a high degree of protection on its own.
與我們假設 Google 的底層系統容易發生故障類似，我們也假設我們的任何保護機制都受到同樣力量的影響，並且可能以同樣的方式、在最不方便的時候發生故障。在大規模下維持資料完整性的保證，是一項因相關軟體系統變化率高而變得更加複雜的挑戰，這需要許多互補但解耦的實踐，每種實踐都經過選擇，以便自身能提供高度的保護。

## The 24 Combinations of Data Integrity Failure Modes
## 24 種資料完整性故障模式組合

Given the many ways data can be lost (as described previously), there is no silver bullet that guards against the many combinations of failure modes. Instead, you need defense in depth. Defense in depth comprises multiple layers, with each successive layer of defense conferring protection from progressively less common data loss scenarios. Figure 26-4 illustrates an object’s journey from soft deletion to destruction, and the data recovery strategies that should be employed along this journey to ensure defense in depth.
鑑於資料可能以多種方式遺失（如前所述），沒有任何單一的解決方案可以防範多種故障模式的組合。相反地，你需要深度防禦 (defense in depth)。深度防禦由多個層次組成，每個後續的防禦層都為越來越不常見的資料遺失情境提供保護。圖 26-4 說明了一個物件從軟刪除到銷毀的過程，以及在此過程中應採用的資料恢復策略，以確保深度防禦。

The first layer is soft deletion (or "lazy deletion" in the case of developer API offerings), which has proven to be an effective defense against inadvertent data deletion scenarios. The second line of defense is backups and their related recovery methods . The third and final layer is regular data validation , covered in Third Layer: Early Detection . Across all these layers, the presence of replication is occasionally useful for data recovery in specific scenarios (although data recovery plans should not rely upon replication).
第一層是軟刪除 (soft deletion)（或在開發者 API 產品中稱為「延遲刪除 (lazy deletion)」），這已被證明是防範無意中刪除資料情境的有效防禦措施。第二道防線是備份及其相關的恢復方法。第三層也是最後一層是定期資料驗證，這在「第三層：早期偵測」中會有所涵蓋。在所有這些層次中，複製 (replication) 的存在偶爾在特定的資料恢復情境中很有用（儘管資料恢復計畫不應依賴於複製）。

## First Layer: Soft Deletion
## 第一層：軟刪除 (Soft Deletion)

When velocity is high and privacy matters, bugs in applications account for the vast majority of data loss and corruption events. In fact, data deletion bugs may become so common that the ability to undelete data for a limited time becomes the primary line of defense against the majority of otherwise permanent, inadvertent data loss.
當開發速度快且隱私重要時，應用程式中的錯誤是造成絕大多數資料遺失和損毀事件的原因。事實上，資料刪除的錯誤可能變得如此普遍，以至於在有限時間內取消刪除資料的能力，成為對抗大多數原本是永久性、無意的資料遺失的主要防線。

Any product that upholds the privacy of its users must allow the users to delete selected subsets and/or all of their data. Such products incur a support burden due to accidental deletion. Giving users the ability to undelete their data (for example, via a trash folder) reduces but cannot completely eliminate this support burden, particularly if your service also supports third-party add-ons that can also delete data.
任何維護使用者隱私的產品都必須允許使用者刪除他們資料的選定子集和/或全部資料。這類產品會因意外刪除而產生支援負擔。給予使用者取消刪除其資料的能力（例如，透過垃圾桶資料夾）可以減少但無法完全消除這種支援負擔，特別是如果你的服務也支援可以刪除資料的第三方附加元件。

Soft deletion can dramatically reduce or even completely eliminate this support burden. Soft deletion means that deleted data is immediately marked as such, rendering it unusable by all but the application’s administrative code paths. Administrative code paths may include legal discovery, hijacked account recovery, enterprise administration, user support, and problem troubleshooting and its related features. Conduct soft deletion when a user empties his or her trash, and provide a user support tool that enables authorized administrators to undelete any items accidentally deleted by users. Google implements this strategy for our most popular productivity applications; otherwise, the user support engineering burden would be untenable.
軟刪除 (Soft deletion) 可以顯著減少甚至完全消除這種支援負擔。軟刪除意味著被刪除的資料會立即被標記，使其除了應用程式的管理程式碼路徑之外，對所有其他路徑都不可用。管理程式碼路徑可能包括法律調查、被盜帳戶恢復、企業管理、使用者支援以及問題疑難排解及其相關功能。當使用者清空他或她的垃圾桶時執行軟刪除，並提供一個使用者支援工具，讓授權管理員能夠取消刪除使用者意外刪除的任何項目。Google 在我們最受歡迎的生產力應用程式中實施了這一策略；否則，使用者支援的工程負擔將難以承受。

You can extend the soft deletion strategy even further by offering users the option to recover deleted data. For example, the Gmail trash bin allows users to access messages that were deleted fewer than 30 days ago.
你可以進一步擴展軟刪除 (soft deletion) 策略，為使用者提供恢復已刪除資料的選項。例如，Gmail 的垃圾桶允許使用者存取 30 天內刪除的郵件。

Another common source of unwanted data deletion occurs as a result of account hijacking. In account hijacking scenarios, a hijacker commonly deletes the original user’s data before using the account for spamming and other unlawful purposes. When you combine the commonality of accidental user deletion with the risk of data deletion by hijackers, the case for a programmatic soft deletion and undeletion interface within and/or beneath your application becomes clear.
另一個常見的非預期資料刪除來源是帳戶被盜。在帳戶被盜的情況下，駭客通常會在利用該帳戶進行垃圾郵件發送和其他非法活動之前，刪除原始使用者的資料。當你將使用者意外刪除的普遍性與駭客刪除資料的風險結合起來考慮時，在你的應用程式內部和/或底層建立一個程式化的軟刪除和取消刪除介面的理由就變得很清楚了。

Soft deletion implies that once data is marked as such, it is destroyed after a reasonable delay. The length of the delay depends upon an organization’s policies and applicable laws, available storage resources and cost, and product pricing and market positioning, especially in cases involving much short-lived data. Common choices of soft deletion delays are 15, 30, 45, or 60 days. In Google’s experience, the majority of account hijacking and data integrity issues are reported or detected within 60 days. Therefore, the case for soft deleting data for longer than 60 days may not be strong.
軟刪除 (Soft deletion) 意味著一旦資料被如此標記，它將在一段合理的延遲後被銷毀。延遲的長度取決於組織的政策和適用法律、可用的儲存資源和成本，以及產品定價和市場定位，特別是在涉及大量短生命週期資料的情況下。軟刪除延遲的常見選擇是 15、30、45 或 60 天。根據 Google 的經驗，大多數帳戶被盜和資料完整性問題在 60 天內被報告或偵測到。因此，將資料軟刪除超過 60 天的理由可能不夠充分。

Google has also found that the most devastating acute data deletion cases are caused by application developers unfamiliar with existing code but working on deletion-related code, especially batch processing pipelines (e.g., an offline MapReduce or Hadoop pipeline). It’s advantageous to design your interfaces to hinder developers unfamiliar with your code from circumventing soft deletion features with new code. One effective way of achieving this is to implement cloud computing offerings that include built-in soft deletion and undeletion APIs, making sure to enable said feature . 128 Even the best armor is useless if you don’t put it on.
Google 還發現，最具破壞性的急性資料刪除案例是由不熟悉現有程式碼但正在處理刪除相關程式碼的應用程式開發人員引起的，特別是批次處理管道（例如，離線的 MapReduce 或 Hadoop 管道）。設計你的介面以阻止不熟悉你程式碼的開發人員用新程式碼規避軟刪除 (soft deletion) 功能是有利的。實現這一點的一個有效方法是實作包含內建軟刪除和取消刪除 API 的雲端運算產品，並確保啟用該功能。128 即使是最好的盔甲，如果你不穿上它，也是沒有用的。

Soft deletion strategies cover data deletion features in consumer products like Gmail or Google Drive, but what if you support a cloud computing offering instead? Assuming your cloud computing offering already supports a programmatic soft deletion and undeletion feature with reasonable defaults, the remaining accidental data deletion scenarios will originate in mistakes made by your own internal developers or your developer customers.
軟刪除 (Soft deletion) 策略涵蓋了像 Gmail 或 Google 雲端硬碟這類消費性產品中的資料刪除功能，但如果你支援的是一個雲端運算產品呢？假設你的雲端運算產品已經支援一個具有合理預設值的程式化軟刪除和取消刪除功能，那麼剩餘的意外資料刪除情境將源於你自己的內部開發人員或你的開發者客戶所犯的錯誤。

In such cases, it can be useful to introduce an additional layer of soft deletion, which we will refer to as "lazy deletion." You can think of lazy deletion as behind the scenes purging, controlled by the storage system (whereas soft deletion is controlled by and expressed to the client application or service). In a lazy deletion scenario, data that is deleted by a cloud application becomes immediately inaccessible to the application, but is preserved by the cloud service provider for up to a few weeks before destruction. Lazy deletion isn’t advisable in all defense in depth strategies: a long lazy deletion period is costly in systems with much short-lived data, and impractical in systems that must guarantee destruction of deleted data within a reasonable time frame (i.e., those that offer privacy guarantees).
在這種情況下，引入一個額外的軟刪除層級，我們稱之為「延遲刪除 (lazy deletion)」，可能會很有用。你可以將延遲刪除想像成由儲存系統控制的幕後清除（而軟刪除是由客戶端應用程式或服務控制並向其表達的）。在延遲刪除的情境中，被雲端應用程式刪除的資料會立即對該應用程式變得不可存取，但會被雲端服務提供者保留長達數週後才銷毀。延遲刪除並非在所有深度防禦 (defense in depth) 策略中都是可取的：在擁有大量短生命週期資料的系統中，長的延遲刪除週期成本高昂，而在必須保證在合理時間範圍內銷毀已刪除資料的系統中（即那些提供隱私保證的系統）則不切實際。

To sum up the first layer of defense in depth:
總結深度防禦 (defense in depth) 的第一層：

A trash folder that allows users to undelete data is the primary defense against user error. Soft deletion is the primary defense against developer error and the secondary defense against user error. In developer offerings, lazy deletion is the primary defense against internal developer error and the secondary defense against external developer error.
垃圾桶資料夾允許使用者取消刪除資料，是防範使用者錯誤的主要防線。軟刪除 (Soft deletion) 是防範開發者錯誤的主要防線，也是防範使用者錯誤的次要防線。在開發者產品中，延遲刪除 (lazy deletion) 是防範內部開發者錯誤的主要防線，也是防範外部開發者錯誤的次要防線。

- A trash folder that allows users to undelete data is the primary defense against user error.
- 一個允許使用者復原已刪除資料的垃圾桶資料夾，是防範使用者錯誤的主要防線。

- Soft deletion is the primary defense against developer error and the secondary defense against user error.
- 軟刪除 (Soft deletion) 是防範開發者錯誤的主要防線，也是防範使用者錯誤的次要防線。

- In developer offerings, lazy deletion is the primary defense against internal developer error and the secondary defense against external developer error.
- 在開發者產品中，延遲刪除 (lazy deletion) 是防範內部開發者錯誤的主要防線，也是防範外部開發者錯誤的次要防線。

What about revision history ? Some products provide the ability to revert items to previous states. When such a feature is available to users, it is a form of trash. When available to developers, it may or may not substitute for soft deletion, depending on its implementation.
那麼修訂歷史 (revision history) 呢？有些產品提供了將項目還原到先前狀態的能力。當這樣的功能對使用者可用時，它是一種垃圾桶的形式。當對開發者可用時，它可能可以也可能不可以替代軟刪除 (soft deletion)，這取決於它的實作方式。

At Google, revision history has proven useful in recovering from certain data corruption scenarios, but not in recovering from most data loss scenarios involving accidental deletion, programmatic or otherwise. This is because some revision history implementations treat deletion as a special case in which previous states must be removed, as opposed to mutating an item whose history may be retained for a certain time period. To provide adequate protection against unwanted deletion, apply the lazy and/or soft deletion principles to revision history also.
在 Google，修訂歷史 (revision history) 已被證明在從某些資料損毀情境中恢復時很有用，但在從大多數涉及意外刪除（無論是程式化的還是其他的）的資料遺失情境中恢復時則不然。這是因為一些修訂歷史的實作將刪除視為一種特殊情況，其中先前的狀態必須被移除，而不是修改一個其歷史可能被保留一段時間的項目。為了提供對非預期刪除的足夠保護，也應將延遲 (lazy) 和/或軟刪除 (soft deletion) 的原則應用於修訂歷史。

## Second Layer: Backups and Their Related Recovery Methods
## 第二層：備份及其相關恢復方法

Backups and data recovery are the second line of defense after soft deletion. The most important principle in this layer is that backups don’t matter; what matters is recovery. The factors supporting successful recovery should drive your backup decisions, not the other way around.
備份和資料恢復是繼軟刪除 (soft deletion) 後的第二道防線。這一層最重要的原則是，備份本身並不重要；重要的是恢復。支持成功恢復的因素應該驅動你的備份決策，而不是反過來。

In other words, the scenarios in which you want your backups to help you recover should dictate the following:
換句話說，你希望備份在哪些情境下幫助你恢復，應該決定以下事項：

Which backup and recovery methods to use How frequently you establish restore points by taking full or incremental backups of your data Where you store backups How long you retain backups
使用哪種備份和恢復方法、你多久透過完整或增量備份建立恢復點、你將備份儲存在哪裡、你保留備份多久。

- Which backup and recovery methods to use
- 使用哪種備份和恢復方法

- How frequently you establish restore points by taking full or incremental backups of your data
- 你多久透過完整或增量備份建立恢復點

- Where you store backups
- 你將備份儲存在哪裡

- How long you retain backups
- 你保留備份多久

How much recent data can you afford to lose during a recovery effort? The less data you can afford to lose, the more serious you should be about an incremental backup strategy. In one of Google’s most extreme cases, we used a near-real-time streaming backup strategy for an older version of Gmail.
在恢復工作中，你能承受多少近期資料的損失？你能承受的資料損失越少，你就應該越認真地對待增量備份策略。在 Google 一個最極端的案例中，我們為舊版 Gmail 使用了近乎即時的串流備份策略。

Even if money isn’t a limitation, frequent full backups are expensive in other ways. Most notably, they impose a compute burden on the live datastores of your service while it’s serving users, driving your service closer to its scalability and performance limits. To ease this burden, you can take full backups during off-peak hours, and then a series of incremental backups when your service is busier.
即使金錢不是限制，頻繁的完整備份在其他方面也很昂貴。最值得注意的是，它們會在你服務的即時資料儲存庫為使用者提供服務時增加計算負擔，使你的服務更接近其可擴展性和效能極限。為了減輕這種負擔，你可以在離峰時段進行完整備份，然後在服務較繁忙時進行一系列的增量備份。

How quickly do you need to recover? The faster your users need to be rescued, the more local your backups should be. Often Google retains costly but quick-to-restore snapshots 129 for very short periods of time within the storage instance, and stores less recent backups on random access distributed storage within the same (or nearby) datacenter for a slightly longer time. Such a strategy alone would not protect from site-level failures, so those backups are often transferred to nearline or offline locations for a longer time period before they’re expired in favor of newer backups.
你需要多快恢復？你的使用者需要越快被拯救，你的備份就應該越本地化。Google 通常會在儲存實例中保留昂貴但能快速恢復的快照 129 很短一段時間，並將較不近期的備份儲存在同一個（或附近）資料中心內的隨機存取分散式儲存上稍長一段時間。單靠這樣的策略無法防範站點級別的故障，所以這些備份通常會被轉移到近線 (nearline) 或離線位置更長一段時間，然後才會因為有更新的備份而過期。

How far back should your backups reach? Your backup strategy becomes more costly the further back you reach, while the scenarios from which you can hope to recover increase (although this increase is subject to diminishing returns).
你的備份應該追溯到多遠？你的備份策略回溯得越遠，成本就越高，而你希望能從中恢復的情境也隨之增加（儘管這種增加會受到邊際效益遞減的影響）。

In Google’s experience, low-grade data mutation or deletion bugs within application code demand the furthest reaches back in time, as some of those bugs were noticed months after the first data loss began. Such cases suggest that you’d like the ability to reach back in time as far as possible.
根據 Google 的經驗，應用程式碼中低度的資料突變或刪除錯誤，需要回溯到最久遠的時間點，因為有些錯誤是在首次資料遺失發生數月後才被注意到。這種情況表明，你會希望能夠盡可能地回溯時間。

On the flip side, in a high-velocity development environment, changes to code and schema may render older backups expensive or impossible to use. Furthermore, it is challenging to recover different subsets of data to different restore points, because doing so would involve multiple backups. Yet, that is exactly the sort of recovery effort demanded by low-grade data corruption or deletion scenarios.
另一方面，在一個高速開發的環境中，程式碼和結構描述的變更可能會使較舊的備份變得昂貴或無法使用。此外，將不同的資料子集恢復到不同的還原點是具有挑戰性的，因為這樣做會涉及多個備份。然而，這正是低度資料損毀或刪除情境所需要的那種恢復工作。

The strategies described in Third Layer: Early Detection are meant to speed detection of low-grade data mutation or deletion bugs within application code, at least partly warding off the need for this type of complex recovery effort. Still, how do you confer reasonable protection before you know what kinds of issues to detect? Google chose to draw the line between 30 and 90 days of backups for many services. Where a service falls within this window depends on its tolerance for data loss and its relative investments in early detection.
在「第三層：早期偵測」中描述的策略，旨在加速偵測應用程式碼中的低度資料突變或刪除錯誤，至少部分地避免了這種複雜的恢復工作的需要。然而，在你了解要偵測哪些類型的問題之前，如何提供合理的保護呢？對於許多服務，Google 選擇將備份的保留期限設定在 30 到 90 天之間。一個服務落在哪個範圍內，取決於它對資料遺失的容忍度以及在早期偵測方面的相對投資。

To sum up our advice for guarding against the 24 combinations of data integrity failure modes: addressing a broad range of scenarios at reasonable cost demands a tiered backup strategy. The first tier comprises many frequent and quickly restored backups stored closest to the live datastores, perhaps using the same or similar storage technologies as the data sources. Doing so confers protection from the majority of scenarios involving software bugs and developer error. Due to relative expense, backups are retained in this tier for anywhere from hours to single-digit days, and may take minutes to restore.
總結我們對於防範 24 種資料完整性故障模式組合的建議：以合理的成本應對廣泛的情境需要分層的備份策略。第一層包含許多頻繁且能快速還原的備份，儲存在最接近即時資料儲存庫的地方，可能使用與資料來源相同或相似的儲存技術。這樣做可以防範大多數涉及軟體錯誤和開發人員錯誤的情境。由於相對昂貴，此層的備份保留時間從數小時到個位數天不等，還原可能需要幾分鐘。

The second tier comprises fewer backups retained for single-digit or low double-digit days on random access distributed filesystems local to the site. These backups may take hours to restore and confer additional protection from mishaps affecting particular storage technologies in your serving stack, but not the technologies used to contain the backups. This tier also protects against bugs in your application that are detected too late to rely upon the first tier of your backup strategy. If you are introducing new versions of your code to production twice a week, it may make sense to retain these backups for at least a week or two before deleting them.
第二層包含較少的備份，保留在站點本地的隨機存取分散式檔案系統上，為期個位數或低兩位數天。這些備份可能需要數小時才能恢復，並能提供額外的保護，以應對影響你服務堆疊中特定儲存技術，但不會影響包含備份的技術的意外事件。這一層還可以防範應用程式中發現得太晚，以至於無法依賴第一層備份策略的錯誤。如果你每週向生產環境推出兩次新版本的程式碼，那麼在刪除這些備份之前，將它們保留至少一到兩週可能是合理的。

Subsequent tiers take advantage of nearline storage such as dedicated tape libraries and offsite storage of the backup media (e.g., tapes or disk drives). Backups in these tiers confer protection against site-level issues, such as a datacenter power outage or distributed filesystem corruption due to a bug.
後續的層級利用近線 (nearline) 儲存，例如專用的磁帶櫃和備份媒體（如磁帶或磁碟機）的異地儲存。這些層級的備份可以防範站點級別的問題，例如資料中心停電或由於錯誤導致的分散式檔案系統損毀。

It is expensive to move large amounts of data to and from tiers. On the other hand, storage capacity at the later tiers does not contend with growth of the live production storage instances of your service. As a result, backups in these tiers tend to be taken less frequently but retained longer.
在各層之間移動大量資料是昂貴的。另一方面，後期層級的儲存容量不會與你服務的即時生產儲存實例的增長相競爭。因此，這些層級的備份往往頻率較低，但保留時間較長。

## Overarching Layer: Replication
## 總體層：複製 (Replication)

In an ideal world, every storage
      instance, including the instances containing your backups, would be replicated. During a data recovery effort, the last thing you want is to discover is that your backups themselves lost the needed data or that the datacenter containing the most useful backup is under maintenance.
在理想世界中，每個儲存實例，包括包含你備份的實例，都應該被複製。在資料恢復工作中，你最不想發現的就是你的備份本身遺失了所需的資料，或者包含最有用備份的資料中心正在進行維護。

As the volume of data increases, replication of every storage instance isn’t always feasible. In such cases, it makes sense to stagger successive backups across different sites, each of which may fail independently, and to write your backups using a redundancy method such as RAID, Reed-Solomon erasure codes, or GFS-style replication. 130
隨著資料量的增加，複製每個儲存實例並非總是可行的。在這種情況下，將連續的備份錯開到不同的站點是合理的，每個站點都可能獨立發生故障，並使用冗餘方法（如 RAID、里德-所羅門糾刪碼或 GFS 風格的複製）來寫入你的備份。130

When choosing a system of redundancy, don’t rely upon an infrequently used scheme whose only "tests" of efficacy are your own infrequent data recovery attempts. Instead, choose a popular scheme that’s in common and continual use by many of its users.
在選擇冗餘系統時，不要依賴一個不常用的方案，其有效性的唯一「測試」就是你自己不頻繁的資料恢復嘗試。相反地，應該選擇一個受歡迎的、被許多使用者普遍且持續使用的方案。

## 1T Versus 1E: Not "Just" a Bigger Backup
## 1T 與 1E：不僅僅是更大的備份

Processes and practices applied to volumes of data measured in T (terabytes) don’t scale well to data measured in E (exabytes). Validating, copying, and performing round-trip tests on a few gigabytes of structured data is an interesting problem. However, assuming that you have sufficient knowledge of your schema and transaction model, this exercise doesn’t present any special challenges. You typically just need to procure the machine resources to iterate over your data, perform some validation logic, and delegate enough storage to hold a few copies of your data.
應用於以 T（太位元組）為單位測量的資料量的流程和實踐，在擴展到以 E（艾位元組）為單位的資料時效果不佳。驗證、複製和對幾 GB 的結構化資料執行來回測試是一個有趣的問題。然而，假設你對你的結構描述和交易模型有足夠的了解，這個練習並不會帶來任何特殊的挑戰。你通常只需要採購機器資源來迭代你的資料，執行一些驗證邏輯，並分配足夠的儲存空間來存放幾份資料副本。

Now let’s up the ante: instead of a few gigabytes, let’s try securing and validating 700 petabytes of structured data. Assuming ideal SATA 2.0 performance of 300 MB/s, a single task that iterates over all of your data and performs even the most basic of validation checks will take 8 decades. Making a few full backups, assuming you have the media, is going to take at least as long. Restore time, with some post-processing, will take even longer. We’re now looking at almost a full century to restore a backup that was up to 80 years old when you started the restore. Obviously, such a strategy needs to be rethought.
現在讓我們提高賭注：與其處理幾 GB，不如試著保護和驗證 700 PB 的結構化資料。假設理想的 SATA 2.0 效能為 300 MB/s，一個迭代所有資料並執行最基本驗證檢查的單一任務將需要 80 年。製作幾個完整備份，假設你有媒體，也將花費至少同樣長的時間。還原時間，加上一些後處理，將花費更長的時間。我們現在面臨的是，要花將近一個世紀的時間來還原一個在你開始還原時就已經高達 80 年老的備份。顯然，這樣的策略需要重新思考。

The most common and largely effective technique used to back up massive amounts of data is to establish "trust points" in your data portions of your stored data that are verified after being rendered immutable, usually by the passage of time. Once we know that a given user profile or transaction is fixed and won’t be subject to further change, we can verify its internal state and make suitable copies for recovery purposes. You can then make incremental backups that only include data that has been modified or added since your last backup. This technique brings your backup time in line with your "mainline" processing time, meaning that frequent incremental backups can save you from the 80-year monolithic verify and copy job.
備份大量資料最常用且大致有效的技術是在你的資料中建立「信任點」——即在儲存的資料中，經過時間推移變得不可變後被驗證的部分。一旦我們知道某個使用者設定檔或交易是固定的，不會再有進一步的變更，我們就可以驗證其內部狀態，並為恢復目的製作適當的副本。然後你可以進行增量備份，只包含自上次備份以來修改或新增的資料。這項技術使你的備份時間與你的「主線」處理時間保持一致，這意味著頻繁的增量備份可以讓你免於長達 80 年的單體驗證和複製工作。

However, remember that we care about restores , not backups. Let’s say that we took a full backup three years ago and have been making daily incremental backups since. A full restore of our data will serially process a chain of over 1,000 highly interdependent backups. Each independent backup incurs additional risk of failure, not to mention the logistical burden of scheduling and the runtime cost of those jobs.
然而，請記住，我們關心的是恢復 (restores)，而不是備份。假設我們三年前做了一次完整備份，此後每天都做增量備份。一次完整的資料恢復將會串行處理一個由超過 1000 個高度相互依賴的備份組成的鏈。每個獨立的備份都會帶來額外的失敗風險，更不用說排程的後勤負擔和這些工作的執行時間成本了。

Another way we can reduce the wall time of our copying and verification jobs is to distribute the load. If we shard our data well, it’s possible to run N tasks in parallel, with each task responsible for copying and verifying 1/ N th of our data. Doing so requires some forethought and planning in the schema design and the physical deployment of our data in order to:
另一種減少我們複製和驗證工作牆上時間的方法是分散負載。如果我們能很好地對資料進行分片 (shard)，就有可能並行執行 N 個任務，每個任務負責複製和驗證我們資料的 1/N。這樣做需要在結構描述設計和資料的實體部署中進行一些深思熟慮和規劃，以便：

Balance the data correctly Ensure the independence of each shard Avoid contention among the concurrent sibling tasks
正確地平衡資料、確保每個分片的獨立性、避免並行的同級任務之間的競爭。

- Balance the data correctly
- 正確地平衡資料

- Ensure the independence of each shard
- 確保每個分片的獨立性

- Avoid contention among the concurrent sibling tasks
- 避免並行的同級任務之間的競爭

Between distributing the load horizontally and restricting the work to vertical slices of the data demarcated by time, we can reduce those eight decades of wall time by several orders of magnitude, rendering our restores relevant.
透過水平分散負載和將工作限制在按時間劃分的資料垂直切片上，我們可以將那八十年的牆上時間減少幾個數量級，使我們的恢復變得有意義。

## Third Layer: Early Detection
## 第三層：早期偵測

“Bad” data doesn’t sit idly by, it propagates. References to missing or corrupt data are copied, links fan out, and with every update the overall quality of your datastore goes down. Subsequent dependent transactions and potential data format changes make restoring from a given backup more difficult as the clock ticks. The sooner you know about a data loss, the easier and more complete your recovery can be.
「壞」資料不會閒置，它會傳播。對遺失或損毀資料的引用會被複製，連結會擴散出去，每次更新都會降低你資料儲存庫的整體品質。隨後的相依交易和潛在的資料格式變更，使得隨著時間的推移，從給定的備份中還原變得更加困難。你越早知道資料遺失，你的恢復就越容易、越完整。

### Challenges faced by cloud developers
### 雲端開發者面臨的挑戰

In high-velocity environments, cloud application and infrastructure services face many data integrity challenges at runtime, such as:
在高速環境中，雲端應用程式和基礎設施服務在執行時面臨許多資料完整性挑戰，例如：

Referential integrity between datastores Schema changes Aging code Zero-downtime data migrations Evolving integration points with other services
資料儲存庫之間的參考完整性、結構描述變更、老舊程式碼、零停機資料遷移、與其他服務不斷演進的整合點。

- Referential integrity between datastores
- 資料儲存庫之間的參考完整性

- Schema changes
- 結構描述變更

- Aging code
- 老舊程式碼

- Zero-downtime data migrations
- 零停機資料遷移

- Evolving integration points with other services
- 與其他服務不斷演進的整合點

Without conscious engineering effort to track emerging relationships in its data, the data quality of a successful and growing service degrades over time.
如果沒有有意識的工程努力來追蹤其資料中新出現的關係，一個成功且不斷成長的服務的資料品質會隨著時間的推移而下降。

Often, the novice cloud developer who chooses a distributed consistent storage API (such as Megastore) delegates the integrity of the application’s data to the distributed consistent algorithm implemented beneath the API (such as Paxos; see Managing Critical State: Distributed Consensus for Reliability ). The developer reasons that the selected API alone will keep the application’s data in good shape. As a result, they unify all application data into a single storage solution that guarantees distributed consistency, avoiding referential integrity problems in exchange for reduced performance and/or scale.
通常，選擇分散式一致性儲存 API（例如 Megastore）的新手雲端開發人員，會將應用程式資料的完整性委託給 API 底層實作的分散式一致性演算法（例如 Paxos；請參閱「管理關鍵狀態：為可靠性而生的分散式共識」）。開發人員的理由是，單獨選定的 API 將使應用程式的資料保持良好狀態。因此，他們將所有應用程式資料統一到一個保證分散式一致性的單一儲存解決方案中，以避免參考完整性問題，但代價是效能和/或規模的降低。

While such algorithms are infallible in theory, their implementations are often riddled with hacks, optimizations, bugs, and educated guesses. For example: in theory, Paxos ignores failed compute nodes and can make progress as long as a quorum of functioning nodes is maintained. In practice, however, ignoring a failed node may correspond to timeouts, retries, and other failure-handling approaches beneath the particular Paxos implementation [Cha07] . How long should Paxos try to contact an unresponsive node before timing it out? When a particular machine fails (perhaps intermittently) in a certain way, with a certain timing, and at a particular datacenter, unpredictable behavior results. The larger the scale of an application, the more frequently the application is affected, unbeknownst, by such inconsistencies. If this logic holds true even when applied to Paxos implementations (as has been true for Google), then it must be more true for eventually consistent implementations such as Bigtable (which has also shown to be true). Affected applications have no way to know that 100% of their data is good until they check: trust storage systems, but verify !
雖然這樣的演算法在理論上是無懈可擊的，但它們的實作通常充滿了各種取巧、最佳化、錯誤和有根據的猜測。例如：理論上，Paxos 會忽略失敗的計算節點，只要能維持一個功能正常的節點的法定人數 (quorum)，就能繼續進行。然而，在實務中，忽略一個失敗的節點可能對應到特定 Paxos 實作底層的逾時、重試和其他故障處理方法 [Cha07]。Paxos 應該在逾時之前嘗試聯繫一個沒有回應的節點多久？當某台機器以某種方式、在某個時間點、在某個資料中心發生故障（可能是間歇性的），就會產生不可預測的行為。應用程式的規模越大，它就越頻繁地在不知不覺中受到這種不一致性的影響。如果這個邏輯即使應用於 Paxos 實作也是成立的（正如 Google 的情況），那麼對於像 Bigtable 這樣的最終一致性實作來說，它必然更加成立（這也已被證明是真實的）。受影響的應用程式在檢查之前無法知道它們的資料是否 100% 良好：信任儲存系統，但要驗證！

To complicate this problem, in order to recover from low-grade data corruption or deletion scenarios, we must recover different subsets of data to different restore points using different backups, while changes to code and schema may render older backups ineffective in high-velocity environments.
為了從低度資料損毀或刪除情境中恢復，我們必須使用不同的備份將不同的資料子集恢復到不同的還原點，而程式碼和結構描述的變更可能會使較舊的備份在高速環境中失效，這使得問題更加複雜。

### Out-of-band data validation
### 帶外 (Out-of-band) 資料驗證

To prevent data quality from degrading before users’ eyes, and to detect low-grade data corruption or data loss scenarios before they become unrecoverable, a system of out-of-band checks and balances is needed both within and between an application’s datastores.
為了防止資料品質在使用者眼前下降，並在低度資料損毀或資料遺失情境變得無法恢復之前偵測到它們，需要在應用程式的資料儲存庫內部和之間建立一個帶外 (out-of-band) 的檢查與平衡系統。

Most often, these data validation pipelines are implemented as collections of map-reductions or Hadoop jobs. Frequently, such pipelines are added as an afterthought to services that are already popular and successful. Sometimes, such pipelines are first attempted when services reach scalability limits and are rebuilt from the ground up. Google has built validators in response to each of these situations.
大多數情況下，這些資料驗證管道是以 map-reductions 或 Hadoop 工作的集合來實作的。通常，這樣的管道是在服務已經受歡迎且成功之後才作為附加功能加入的。有時，這樣的管道是在服務達到可擴展性極限並從頭開始重建時首次嘗試的。Google 針對這兩種情況都建立了驗證器。

Shunting some developers to work on a data validation pipeline can slow engineering velocity in the short term. However, devoting engineering resources to data validation endows other developers with the courage to move faster in the long run, because the engineers know that data corruption bugs are less likely to sneak into production unnoticed. Similar to the effects enjoyed when units test are introduced early in the project lifecycle, a data validation pipeline results in an overall acceleration of software development projects.
將一些開發人員分流去開發資料驗證管道，短期內可能會減緩工程速度。然而，從長遠來看，投入工程資源進行資料驗證，會讓其他開發人員有勇氣更快地行動，因為工程師們知道資料損毀的錯誤不太可能在生產環境中悄悄溜走而不被發現。與在專案生命週期早期引入單元測試所享有的效果類似，資料驗證管道會帶來軟體開發專案的整體加速。

To cite a specific example: Gmail sports a number of data validators, each of which has detected actual data integrity problems in production. Gmail developers derive comfort from the knowledge that bugs introducing inconsistencies in production data are detected within 24 hours, and shudder at the thought of running their data validators less often than daily. These validators, along with a culture of unit and regression testing and other best practices, have given Gmail developers the courage to introduce code changes to Gmail’s production storage implementation more frequently than once a week.
舉一個具體的例子：Gmail 擁有多個資料驗證器，每一個都在生產環境中偵測到過實際的資料完整性問題。Gmail 開發人員從「引入生產資料不一致性的錯誤會在 24 小時內被偵測到」這一認知中獲得安慰，並且對於每天少於一次運行資料驗證器的想法感到不寒而慄。這些驗證器，連同單元測試、回歸測試的文化以及其他最佳實踐，給予了 Gmail 開發人員每週不止一次地向 Gmail 的生產儲存實作中引入程式碼變更的勇氣。

Out-of-band data validation is tricky to implement correctly. When too strict, even simple, appropriate changes cause validation to fail. As a result, engineers abandon data validation altogether. If the data validation isn’t strict enough, user experience–affecting data corruption can slip through undetected. To find the right balance, only validate invariants that cause devastation to users.
帶外 (Out-of-band) 資料驗證很難正確實作。如果過於嚴格，即使是簡單、適當的變更也會導致驗證失敗。結果，工程師會完全放棄資料驗證。如果資料驗證不夠嚴格，影響使用者體驗的資料損毀可能會在未被偵測到的情況下溜走。為了找到適當的平衡，只驗證那些會對使用者造成災難性後果的不變量 (invariants)。

For example, Google Drive periodically validates that file contents align with listings in Drive folders. If these two elements don’t align, some files would be missing data a disastrous outcome. Drive infrastructure developers were so invested in data integrity that they also enhanced their validators to automatically fix such inconsistencies. This safeguard turned a potential emergency "all-hands-on-deck-omigosh-files-are-disappearing!" data loss situation in 2013 into a business as usual, "let’s go home and fix the root cause on Monday," situation. By transforming emergencies into business as usual, validators improve engineering morale, quality of life, and predictability.
例如，Google 雲端硬碟會定期驗證檔案內容是否與雲端硬碟資料夾中的清單一致。如果這兩個元素不一致，某些檔案就會遺失資料——這是一個災難性的後果。雲端硬碟基礎設施的開發人員非常投入於資料完整性，他們甚至增強了驗證器，使其能夠自動修復這類不一致。這項保護措施將 2013 年一個潛在的緊急「全員出動，天啊，檔案正在消失！」的資料遺失情況，轉變為一個日常業務，「我們回家，週一再來修復根本原因」的情況。透過將緊急情況轉變為日常業務，驗證器提高了工程師的士氣、生活品質和可預測性。

Out-of-band validators can be expensive at scale. A significant portion of Gmail’s compute resource footprint supports a collection of daily validators. To compound this expense, these validators also lower server-side cache hit rates, reducing server-side responsiveness experienced by users. To mitigate this hit to responsiveness, Gmail provides a variety of knobs for rate-limiting its validators and periodically refactors the validators to reduce disk contention. In one such refactoring effort, we cut the contention for disk spindles by 60% without significantly reducing the scope of the invariants they covered. While the majority of Gmail’s validators run daily, the workload of the largest validator is divided into 10–14 shards, with one shard validated per day for reasons of scale.
帶外 (Out-of-band) 驗證器在大規模下可能非常昂貴。Gmail 計算資源足跡的很大一部分支援著一系列日常驗證器。更糟的是，這些驗證器還會降低伺服器端的快取命中率，從而降低使用者體驗到的伺服器端回應速度。為了減輕對回應速度的影響，Gmail 提供了多種旋鈕來限制其驗證器的速率，並定期重構驗證器以減少磁碟競爭。在一次這樣的重構工作中，我們將磁碟主軸的競爭減少了 60%，而沒有顯著減少它們所涵蓋的不變量的範圍。雖然 Gmail 的大多數驗證器每天運行，但出於規模考量，最大驗證器的工作負載被分成 10-14 個分片，每天驗證一個分片。

Google Compute Storage is another example of the challenges scale entails to data validation. When its out-of-band validators could no longer finish within a day, Compute Storage engineers had to devise a more efficient way to verify its metadata than use of brute force alone. Similar to its application in data recovery, a tiered strategy can also be useful in out-of-band data validation. As a service scales, sacrifice rigor in daily validators. Make sure that daily validators continue to catch the most disastrous scenarios within 24 hours, but continue with more rigorous validation at reduced frequency to contain costs and latency.
Google Compute Storage 是規模對資料驗證帶來挑戰的另一個例子。當其帶外 (out-of-band) 驗證器無法在一天內完成時，Compute Storage 的工程師必須設計出比單純使用暴力法更有效率的方法來驗證其元資料。與其在資料恢復中的應用類似，分層策略在帶外資料驗證中也很有用。隨著服務規模的擴大，犧牲日常驗證器的嚴謹性。確保日常驗證器能在 24 小時內繼續捕捉到最災難性的情境，但以較低的頻率繼續進行更嚴格的驗證，以控制成本和延遲。

Troubleshooting failed validations can take significant effort. Causes of an intermittent failed validation could vanish within minutes, hours, or days. Therefore, the ability to rapidly drill down into validation audit logs is essential. Mature Google services provide on-call engineers with comprehensive documentation and tools to troubleshoot. For example, on-call engineers for Gmail are provided with:
對失敗的驗證進行疑難排解可能需要大量精力。間歇性驗證失敗的原因可能在幾分鐘、幾小時或幾天內消失。因此，快速深入研究驗證稽核日誌的能力至關重要。成熟的 Google 服務為值班工程師提供全面的文件和工具來進行疑難排解。例如，Gmail 的值班工程師會被提供：

A suite of playbook entries describing how to respond to a validation failure alert A BigQuery-like investigation tool A data validation dashboard
一套描述如何回應驗證失敗警報的教戰手冊 (playbook) 條目、一個類似 BigQuery 的調查工具、一個資料驗證儀表板。

- A suite of playbook entries describing how to respond to a validation failure alert
- 一套描述如何回應驗證失敗警報的教戰手冊 (playbook) 條目

- A BigQuery-like investigation tool
- 一個類似 BigQuery 的調查工具

- A data validation dashboard
- 一個資料驗證儀表板

Effective out-of-band data validation demands all of the following:
有效的帶外 (out-of-band) 資料驗證需要以下所有條件：

Validation job management Monitoring, alerts, and dashboards Rate-limiting features Troubleshooting tools Production playbooks Data validation APIs that make validators easy to add and refactor
驗證工作管理、監控、警報和儀表板、速率限制功能、疑難排解工具、生產教戰手冊 (playbooks)、使驗證器易於新增和重構的資料驗證 API。

- Validation job management
- 驗證工作管理

- Monitoring, alerts, and dashboards
- 監控、警報和儀表板

- Rate-limiting features
- 速率限制功能

- Troubleshooting tools
- 疑難排解工具

- Production playbooks
- 生產教戰手冊 (Production playbooks)

- Data validation APIs that make validators easy to add and refactor
- 使驗證器易於新增和重構的資料驗證 API

The majority of small engineering teams operating at high velocity can’t afford to design, build, and maintain all of these systems. If they are pressured to do so, the result is often fragile, limited, and wasteful one-offs that fall quickly into disrepair. Therefore, structure your engineering teams such that a central infrastructure team provides a data validation framework for multiple product engineering teams. The central infrastructure team maintains the out-of-band data validation framework, while the product engineering teams maintain the custom business logic at the heart of the validator to keep pace with their evolving products.
大多數高速運作的小型工程團隊無法負擔設計、建立和維護所有這些系統。如果他們被迫這樣做，結果往往是脆弱、有限且浪費的一次性產品，很快就會失修。因此，應該這樣組織你的工程團隊：由一個中央基礎設施團隊為多個產品工程團隊提供一個資料驗證框架。中央基礎設施團隊維護帶外 (out-of-band) 資料驗證框架，而產品工程團隊則維護驗證器核心的客製化業務邏輯，以跟上他們不斷發展的產品。

## Knowing That Data Recovery Will Work
## 確保資料恢復會成功

When does a light bulb break? When flicking the switch fails to turn on the light? Not always often the bulb had already failed, and you simply notice the failure at the unresponsive flick of the switch. By then, the room is dark and you’ve stubbed your toe.
燈泡什麼時候壞掉？是當你按開關卻無法開燈的時候嗎？不總是如此——通常燈泡早就壞了，你只是在按下開關沒有反應時才注意到故障。到那時，房間已經一片漆黑，而你也踢到了腳趾。

Likewise, your recovery dependencies (meaning mostly, but not only, your backup), may be in a latent broken state, which you aren’t aware of until you attempt to recover data.
同樣地，你的恢復依賴項（主要指但不限於你的備份），可能處於潛在的損壞狀態，直到你嘗試恢復資料時才會意識到。

If you discover that your restore process is broken before you need to rely upon it, you can address the vulnerability before you fall victim to it: you can take another backup, provision additional resources, and change your SLO. But to take these actions proactively, you first have to know they’re needed. To detect these vulnerabilities:
如果你在需要依賴恢復流程之前就發現它已經損壞，你可以在你成為受害者之前解決這個漏洞：你可以再做一次備份、配置額外的資源，並更改你的服務等級目標 (SLO)。但要主動採取這些行動，你首先必須知道它們是必要的。要偵測這些漏洞：

Continuously test the recovery process as part of your normal operations Set up alerts that fire when a recovery process fails to provide a heartbeat indication of its success
持續測試恢復流程作為你正常運作的一部分、設定警報，當恢復流程未能提供其成功的「心跳」指示時觸發。

- Continuously test the recovery process as part of your normal operations
- 持續測試恢復流程作為你正常運作的一部分

- Set up alerts that fire when a recovery process fails to provide a heartbeat indication of its success
- 設定警報，當恢復流程未能提供其成功的「心跳」指示時觸發

What can go wrong with your recovery process? Anything and everything which is why the only test that should let you sleep at night is a full end-to-end test. Let the proof be in the pudding. Even if you recently ran a successful recovery, parts of your recovery process can still break. If you take away just one lesson from this chapter, remember that you only know that you can recover your recent state if you actually do so .
你的恢復過程可能會出什麼問題？任何事和所有事——這就是為什麼唯一能讓你高枕無憂的測試是完整的端到端測試。讓實踐來證明一切。即使你最近成功地進行了一次恢復，你的恢復過程的某些部分仍然可能出錯。如果你從本章中只學到一件事，請記住，只有當你真正做到了，你才知道你能恢復你最近的狀態。

If recovery tests are a manual, staged event, testing becomes an unwelcome bit of drudgery that isn’t performed either deeply or frequently enough to deserve your confidence. Therefore, automate these tests whenever possible and then run them continuously.
如果恢復測試是一個手動的、分階段的事件，那麼測試就會變成一件不受歡迎的苦差事，其執行深度和頻率都不足以讓你產生信心。因此，應盡可能自動化這些測試，然後持續運行它們。

The aspects of your recovery plan you should confirm are myriad:
你應該確認的恢復計畫的方面有很多：

Are your backups valid and complete, or are they empty? Do you have sufficient machine resources to run all of the setup, restore, and post-processing tasks that comprise your recovery? Does the recovery process complete in reasonable wall time? Are you able to monitor the state of your recovery process as it
        progresses? Are you free of critical dependencies on resources outside of your
        control, such as access to an offsite media storage vault that isn’t
        available 24/7?
你的備份是有效和完整的，還是空的？你有足夠的機器資源來執行構成你恢復的所有設定、還原和後處理任務嗎？恢復過程是否在合理的牆上時間內完成？你是否能夠在恢復過程進行時監控其狀態？你是否沒有不受你控制的資源的關鍵依賴，例如無法 24/7 存取的異地媒體儲存庫？

- Are your backups valid and complete, or are they empty?
- 你的備份是有效和完整的，還是空的？

- Do you have sufficient machine resources to run all of the setup, restore, and post-processing tasks that comprise your recovery?
- 你有足夠的機器資源來執行構成你恢復的所有設定、還原和後處理任務嗎？

- Does the recovery process complete in reasonable wall time?
- 恢復過程是否在合理的牆上時間內完成？

- Are you able to monitor the state of your recovery process as it progresses?
- 你是否能夠在恢復過程進行時監控其狀態？

- Are you free of critical dependencies on resources outside of your control, such as access to an offsite media storage vault that isn’t available 24/7?
- 你是否沒有不受你控制的資源的關鍵依賴，例如無法 24/7 存取的異地媒體儲存庫？

Our testing has discovered the aforementioned failures, as well as failures of many other components of a successful data recovery. If we hadn’t discovered these failures in regular tests that is, if we came across the failures only when we needed to recover user data in real emergencies it’s quite possible that some of Google’s most successful products today may not have stood the test of time.
我們的測試發現了上述故障，以及成功資料恢復的許多其他元件的故障。如果我們沒有在定期測試中發現這些故障——也就是說，如果我們只有在真正緊急情況下需要恢復使用者資料時才遇到這些故障——那麼今天 Google 一些最成功的產品很可能無法經得起時間的考驗。

Failures are inevitable. If you wait to discover them when you’re under the gun, facing a real data loss, you’re playing with fire. If testing forces the failures to happen before actual catastrophe strikes, you can fix problems before any harm comes to fruition .
失敗是不可避免的。如果你等到面臨真正的資料遺失、火燒眉毛時才發現它們，那你就是在玩火。如果測試在實際災難發生前迫使失敗發生，你就可以在任何傷害造成之前解決問題。

# Case Studies
# 案例研究

Life imitates art (or in this case, science), and as we predicted, real life has given us unfortunate and inevitable opportunities to put our data recovery systems and processes to the test, under real-world pressure. Two of the more notable and interesting of these opportunities are discussed here.
生活模仿藝術（或者在這種情況下，是科學），正如我們所預測的，現實生活給了我們不幸且不可避免的機會，在真實世界的壓力下，將我們的資料恢復系統和流程付諸實踐。這裡討論了其中兩個較為顯著和有趣的機會。

## Gmail February, 2011: Restore from GTape
## Gmail 2011 年 2 月：從 GTape 恢復

The first recovery case study we’ll examine was unique in a couple of ways: the number of failures that coincided to bring about the data loss, and the fact that it was the largest use of our last line of defense, the GTape offline backup system.
我們將要研究的第一個恢復案例研究在幾個方面是獨特的：導致資料遺失的故障數量，以及這是我們最後一道防線——GTape 離線備份系統——最大規模的一次使用。

### Sunday, February 27, 2011, late in the evening
### 2011 年 2 月 27 日，星期日，深夜

The Gmail backup system pager is triggered, displaying a phone number to join a conference call. The event we had long feared indeed, the reason for the backup system’s existence has come to pass: Gmail lost a significant amount of user data. Despite the system’s many safeguards and internal checks and redundancies, the data disappeared from Gmail.
Gmail 備份系統的呼叫器被觸發，顯示一個電話號碼以加入電話會議。我們長期以來所擔心的事件——事實上，也是備份系統存在的原因——終於發生了：Gmail 遺失了大量的使用者資料。儘管系統有多重保護措施、內部檢查和冗餘，資料還是從 Gmail 中消失了。

This was the first large-scale use of GTape, a global backup system for Gmail, to restore live customer data. Fortunately, it was not the first such restore, as similar situations had been previously simulated many times. Therefore, we were able to:
這是首次大規模使用 GTape——一個 Gmail 的全球備份系統——來恢復即時客戶資料。幸運的是，這並非首次這樣的恢復，因為類似的情況先前已經模擬過很多次。因此，我們能夠：

Deliver an estimate of how long it would take to restore the majority of the affected user accounts Restore all of the accounts within several hours of our initial estimate Recover 99%+ of the data before the estimated completion time
提供一個估計，恢復大多數受影響使用者帳戶需要多長時間、在我們初步估計的幾小時內恢復所有帳戶、在估計完成時間前恢復 99% 以上的資料。

- Deliver an estimate of how long it would take to restore the majority of the affected user accounts
- 提供一個估計，恢復大多數受影響使用者帳戶需要多長時間

- Restore all of the accounts within several hours of our initial estimate
- 在我們初步估計的幾小時內恢復所有帳戶

- Recover 99%+ of the data before the estimated completion time
- 在估計完成時間前恢復 99% 以上的資料

Was the ability to formulate such an estimate luck? No our success was the fruit of planning, adherence to best practices, hard work, and cooperation, and we were glad to see our investment in each of these elements pay off as well as it did. Google was able to restore the lost data in a timely manner by executing a plan designed according to the best practices of Defense in Depth and Emergency Preparedness .
能夠制定出這樣的估計是運氣嗎？不——我們的成功是規劃、遵守最佳實踐、辛勤工作和合作的成果，我們很高興看到我們在這些方面的投資得到了如此好的回報。Google 能夠及時恢復遺失的資料，是透過執行一個根據深度防禦 (Defense in Depth) 和應急準備 (Emergency Preparedness) 的最佳實踐所設計的計畫。

When Google publicly revealed that we recovered this data from our previously undisclosed tape backup system [Slo11] , public reaction was a mix of surprise and amusement. Tape? Doesn’t Google have lots of disks and a fast network to replicate data this important? Of course Google has such resources, but the principle of Defense in Depth dictates providing multiple layers of protection to guard against the breakdown or compromise of any single protection mechanism. Backing up online systems such as Gmail provides defense in depth at two layers:
當 Google 公開透露我們是從先前未公開的磁帶備份系統中恢復這些資料時 [Slo11]，公眾的反應是驚訝與 amused 的混合。磁帶？Google 不是有很多磁碟和快速的網路來複製這麼重要的資料嗎？當然 Google 有這些資源，但深度防禦 (Defense in Depth) 的原則要求提供多層保護，以防範任何單一保護機制的崩潰或受損。備份像 Gmail 這樣的線上系統，在兩個層面上提供了深度防禦：

A failure of the internal Gmail redundancy and backup subsystems A wide failure or zero-day vulnerability in a device driver or filesystem affecting the underlying storage medium (disk)
Gmail 內部冗餘和備份子系統的故障、影響底層儲存媒介（磁碟）的裝置驅動程式或檔案系統的廣泛故障或零時差漏洞 (zero-day vulnerability)。

- A failure of the internal Gmail redundancy and backup subsystems
- Gmail 內部冗餘和備份子系統的故障

- A wide failure or zero-day vulnerability in a device driver or filesystem affecting the underlying storage medium (disk)
- 影響底層儲存媒介（磁碟）的裝置驅動程式或檔案系統的廣泛故障或零時差漏洞 (zero-day vulnerability)

This particular failure resulted from the first scenario while Gmail had internal means of recovering lost data, this loss went beyond what internal means could recover.
這次特定的故障是由第一種情況造成的——雖然 Gmail 有內部的方法來恢復遺失的資料，但這次的損失超出了內部方法所能恢復的範圍。

One of the most internally celebrated aspects of the Gmail data recovery was the degree of cooperation and smooth coordination that comprised the recovery. Many teams, some completely unrelated to Gmail or data recovery, pitched in to help. The recovery couldn’t have succeeded so smoothly without a central plan to choreograph such a widely distributed Herculean effort; this plan was the product of regular dress rehearsals and dry runs. Google’s devotion to emergency preparedness leads us to view such failures as inevitable. Accepting this inevitability, we don’t hope or bet to avoid such disasters, but anticipate that they will occur. Thus, we need a plan for dealing not only with the foreseeable failures, but for some amount of random undifferentiated breakage, as well.
Gmail 資料恢復中最受內部讚揚的方面之一，是恢復過程中展現出的合作程度和順暢的協調。許多團隊，有些甚至與 Gmail 或資料恢復完全無關，都伸出援手。如果沒有一個中央計畫來精心安排這樣一個廣泛分佈的艱鉅任務，恢復工作不可能如此順利；這個計畫是定期演練和預演的產物。Google 對應急準備的投入使我們將此類故障視為不可避免。接受這種不可避免性，我們不期望或賭注能避免此類災難，而是預期它們會發生。因此，我們需要一個計畫，不僅要處理可預見的故障，還要處理一定數量的隨機、未分化的損壞。

In short, we always knew that adherence to best practices is important, and it was good to see that maxim proven true.
簡而言之，我們一直都知道遵守最佳實踐很重要，很高興看到這條格言被證明是正確的。

## Google Music March 2012: Runaway Deletion Detection
## Google Music 2012 年 3 月：失控刪除偵測

The second failure we’ll examine entails challenges in logistics that are unique to the scale of the datastore being recovered: where do you store over 5,000 tapes, and how do you efficiently (or even feasibly) read that much data from offline media in a reasonable amount of time?
我們將要研究的第二個故障，涉及在恢復資料儲存庫的規模下所特有的後勤挑戰：你如何儲存超過 5,000 卷磁帶，以及你如何有效率地（甚至可行地）在合理的時間內從離線媒體讀取那麼多資料？

### Tuesday, March 6th, 2012, mid-afternoon
### 2012 年 3 月 6 日，星期二，下午三點左右

### Discovering the problem
### 發現問題

A Google Music user reports that previously unproblematic tracks are being skipped. The team responsible for interfacing with Google Music’s users notifies Google Music engineers. The problem is investigated as a possible media streaming issue.
一位 Google Music 使用者回報，先前沒有問題的曲目正在被跳過。負責與 Google Music 使用者介接的團隊通知了 Google Music 工程師。該問題被當作可能的媒體串流問題進行調查。

On March 7th, the investigating engineer discovers that the unplayable track’s metadata is missing a reference that should point to the actual audio data. He is surprised. The obvious fix is to locate the audio data and reinstate the reference to the data. However, Google engineering prides itself for a culture of fixing issues at the root, so the engineer digs deeper.
3 月 7 日，調查工程師發現無法播放的曲目的元資料中缺少一個應該指向實際音訊資料的引用。他很驚訝。顯而易見的修復方法是找到音訊資料並恢復對該資料的引用。然而，Google 工程文化以從根本上解決問題為榮，所以這位工程師深入挖掘。

When he finds the cause of the data integrity lapse, he almost has a heart attack: the audio reference was removed by a privacy-protecting data deletion pipeline. This part of Google Music was designed to delete very large numbers of audio tracks in record time.
當他發現資料完整性失誤的原因時，他差點心臟病發作：音訊引用被一個保護隱私的資料刪除管道移除了。Google Music 的這部分設計是用來在創紀錄的時間內刪除大量音訊軌道的。

### Assessing the damage
### 評估損害

Google’s privacy policy protects a user’s personal data. As applied to Google Music specifically, our privacy policy means that music files and relevant metadata are removed within reasonable time after users delete them. As the popularity of Google Music soared, the amount of data grew rapidly, so the original deletion implementation needed to be redesigned in 2012 to be more efficient. On February 6th, the updated data deletion pipeline enjoyed its maiden run, to remove relevant metadata. Nothing seemed amiss at the time, so a second stage of the pipeline was allowed to remove the associated audio data too.
Google 的隱私政策保護使用者的個人資料。具體應用到 Google Music，我們的隱私政策意味著在使用者刪除音樂檔案和相關元資料後，它們會在合理的時間內被移除。隨著 Google Music 的普及，資料量迅速增長，因此最初的刪除實作需要在 2012 年重新設計以提高效率。2 月 6 日，更新後的資料刪除管道首次運行，以移除相關元資料。當時似乎沒有任何問題，所以管道的第二階段被允許也移除相關的音訊資料。

Could the engineer’s worst nightmare be true? He immediately sounded the alarm, raising the priority of the support case to Google’s most urgent classification and reporting the issue to engineering management and Site Reliability Engineering. A small team of Google Music developers and SREs assembled to tackle the issue, and the offending pipeline was temporarily disabled to stem the tide of external user casualties .
工程師最壞的惡夢會成真嗎？他立即發出警報，將支援案例的優先級提升到 Google 最緊急的分類，並向工程管理部門和網站可靠性工程 (Site Reliability Engineering, SRE) 報告了這個問題。一個由 Google Music 開發人員和 SRE 組成的小團隊集結起來處理這個問題，而有問題的管道被暫時禁用，以阻止外部使用者受害的浪潮。

Next, manually checking the metadata for millions to billions of files organized across multiple datacenters would be unthinkable. So the team whipped up a hasty MapReduce job to assess the damage and waited desperately for the job to complete. They froze as its results came in on March 8th: the refactored data deletion pipeline had removed approximately 600,000 audio references that shouldn’t have been removed, affecting audio files for 21,000 users. Since the hasty diagnosis pipeline made a few simplifications, the true extent of the damage could be worse.
接下來，手動檢查分佈在多個資料中心的數百萬到數十億個檔案的元資料是不可想像的。於是團隊匆忙地建立了一個 MapReduce 工作來評估損害，並焦急地等待工作完成。當 3 月 8 日結果出來時，他們都驚呆了：重構後的資料刪除管道移除了大約 60 萬個不應被移除的音訊引用，影響了 21,000 名使用者的音訊檔案。由於這個倉促的診斷管道做了一些簡化，真實的損害程度可能更糟。

It had been over a month since the buggy data deletion pipeline first ran, and that maiden run itself removed hundreds of thousands of audio tracks that should not have been removed. Was there any hope of getting the data back? If the tracks weren’t recovered, or weren’t recovered fast enough, Google would have to face the music from its users. How could we not have noticed this glitch?
自從那個有問題的資料刪除管道首次運行以來，已經過了一個多月，而那次首次運行本身就移除了數十萬個不應該被移除的音軌。還有希望把資料找回來嗎？如果這些音軌沒有被恢復，或者恢復得不夠快，Google 將不得不面對來自使用者的責難。我們怎麼會沒有注意到這個小故障呢？

### Resolving the issue
### 解決問題

The first step in resolving the issue was to identify the actual bug, and determine how and why the bug happened. As long as the root cause wasn’t identified and fixed, any recovery efforts would be in vain. We would be under pressure to re-enable the pipeline to respect the requests of users who deleted audio tracks, but doing so would hurt innocent users who would continue to lose store-bought music, or worse, their own painstakingly recorded audio files. The only way to escape the Catch-22 131 was to fix the issue at its root, and fix it quickly.
解決問題的第一步是識別實際的錯誤，並確定錯誤是如何以及為何發生的。只要根本原因沒有被識別和修復，任何恢復工作都將是徒勞的。我們將面臨壓力，需要重新啟用管道以尊重刪除音軌的使用者的請求，但這樣做會傷害無辜的使用者，他們將繼續失去商店購買的音樂，或者更糟的是，他們自己辛苦錄製的音訊檔案。擺脫這種第 22 條軍規 (Catch-22) 131 的唯一方法是從根本上解決問題，並且要快。

Yet there was no time to waste before mounting the recovery effort. The audio tracks themselves were backed up to tape, but unlike our Gmail case study, the encrypted backup tapes for Google Music were trucked to offsite storage locations, because that option offered more space for voluminous backups of users’ audio data. To restore the experience of affected users quickly, the team decided to troubleshoot the root cause while retrieving the offsite backup tapes (a rather time-intensive restore option) in parallel.
然而，在展開恢復工作之前，沒有時間可以浪費。音軌本身已備份到磁帶，但與我們的 Gmail 案例研究不同，Google Music 的加密備份磁帶是用卡車運到異地儲存地點的，因為該選項為使用者大量的音訊資料備份提供了更多空間。為了快速恢復受影響使用者的體驗，團隊決定在檢索異地備份磁帶（一個相當耗時的恢復選項）的同時，並行地對根本原因進行疑難排解。

The engineers split into two groups. The most experienced SREs worked on the recovery effort, while the developers analyzed the data deletion code and attempted to fix the data loss bug at its root. Due to incomplete knowledge of the root problem, the recovery would have to be staged in multiple passes. The first batch of nearly half a million audio tracks was identified, and the team that maintained the tape backup system was notified of the emergency recovery effort at 4:34 p.m. Pacific Time on March 8th.
工程師們分成兩組。經驗最豐富的 SRE 負責恢復工作，而開發人員則分析資料刪除程式碼，並試圖從根本上修復資料遺失的錯誤。由於對根本問題的了解不完整，恢復工作必須分多個階段進行。第一批近 50 萬個音軌被識別出來，維護磁帶備份系統的團隊在 3 月 8 日太平洋時間下午 4:34 接到了緊急恢復工作的通知。

The recovery team had one factor working in their favor: this recovery effort occurred just weeks after the company’s annual disaster recovery testing exercise (see [Kri12] ). The tape backup team already knew the capabilities and limitations of their subsystems that had been the subjects of DiRT tests and began dusting off a new tool they’d tested during a DiRT exercise. Using the new tool, the combined recovery team began the painstaking effort of mapping hundreds of thousands of audio files to backups registered in the tape backup system, and then mapping the files from backups to actual tapes.
恢復團隊有一個有利因素：這次恢復工作發生在公司年度災難恢復測試演習（見 [Kri12]）僅幾週後。磁帶備份團隊已經了解他們子系統的能力和限制，這些子系統曾是 DiRT 測試的對象，並開始重新使用他們在 DiRT 演習期間測試過的一個新工具。使用這個新工具，聯合恢復團隊開始了艱鉅的工作，將數十萬個音訊檔案對應到磁帶備份系統中註冊的備份，然後再將檔案從備份對應到實際的磁帶。

In this way, the team determined that the initial recovery effort would involve the recall of over 5,000 backup tapes by truck. Afterwards, datacenter technicians would have to clear out space for the tapes at tape libraries. A long, complex process of registering the tapes and extracting the data from the tapes would follow, involving workarounds and mitigations in the event of bad tapes, bad drives, and unexpected system interactions.
透過這種方式，團隊確定最初的恢復工作將涉及用卡車召回超過 5,000 卷備份磁帶。之後，資料中心技術人員將不得不在磁帶櫃中清出空間來放置這些磁帶。接下來將是一個漫長而複雜的過程，包括註冊磁帶並從中提取資料，其中還涉及在遇到壞磁帶、壞磁碟機和意外系統互動時的變通辦法和緩解措施。

Unfortunately, only 436,223 of the approximately 600,000 lost audio tracks were found on tape backups, which meant that about 161,000 other audio tracks were eaten before they could be backed up. The recovery team decided to figure out how to recover the 161,000 missing tracks after they initiated the recovery process for the tracks with tape backups.
不幸的是，在大約 60 萬個遺失的音軌中，只有 436,223 個在磁帶備份中找到，這意味著大約有 161,000 個其他音軌在它們可以被備份之前就被「吃掉」了。恢復團隊決定在他們啟動有磁帶備份的音軌的恢復過程之後，再想辦法恢復那 161,000 個遺失的音軌。

Meanwhile, the root cause team had pursued and abandoned a red herring: they initially thought that a storage service on which Google Music depended had provided buggy data that misled the data deletion pipelines to remove the wrong audio data. Upon closer investigation, that theory was proven false. The root cause team scratched their heads and continued their search for the elusive bug.
與此同時，根本原因團隊追查並放棄了一個錯誤的線索：他們最初認為 Google Music 所依賴的一個儲存服務提供了有問題的資料，誤導了資料刪除管道，移除了錯誤的音訊資料。經過更深入的調查，這個理論被證明是錯誤的。根本原因團隊搔了搔頭，繼續尋找那個難以捉摸的錯誤。

Once the recovery team had identified the backup tapes, the first recovery wave kicked off on March 8th. Requesting 1.5 petabytes of data distributed among thousands of tapes from offsite storage was one matter, but extracting the data from the tapes was quite another. The custom-built tape backup software stack wasn’t designed to handle a single restore operation of such a large size, so the initial recovery was split into 5,475 restore jobs. It would take a human operator typing in one restore command a minute more than three days to request that many restores, and any human operator would no doubt make many mistakes. Just requesting the restore from the tape backup system needed SRE to develop a programmatic solution. 132
一旦恢復團隊確定了備份磁帶，第一波恢復工作於 3 月 8 日展開。從異地儲存請求分佈在數千卷磁帶上的 1.5 PB 資料是一回事，但從磁帶中提取資料又是另一回事。客製化的磁帶備份軟體堆疊並非設計用來處理如此大規模的單一恢復操作，因此最初的恢復被分成 5,475 個恢復工作。一個人類操作員每分鐘輸入一個恢復命令，需要超過三天的時間才能請求那麼多次恢復，而且任何人類操作員無疑都會犯很多錯誤。光是從磁帶備份系統請求恢復，就需要 SRE 開發一個程式化的解決方案。132

By midnight on March 9th, Music SRE finished requesting all 5,475 restores. The tape backup system began working its magic. Four hours later, it spat out a list of 5,337 backup tapes to be recalled from offsite locations. In another eight hours, the tapes arrived at a datacenter in a series of truck deliveries.
到 3 月 9 日午夜，Music SRE 完成了所有 5,475 次恢復請求。磁帶備份系統開始發揮其魔力。四小時後，它吐出了一份需要從異地召回的 5,337 卷備份磁帶清單。再過八小時，這些磁帶透過一系列卡車運輸抵達了一個資料中心。

While the trucks were en route, datacenter technicians took several tape libraries down for maintenance and removed thousands of tapes to make way for the massive data recovery operation. Then the technicians began painstakingly loading the tapes by hand as thousands of tapes arrived in the wee hours of the morning. In past DiRT exercises, this manual process proved hundreds of times faster for massive restores than the robot-based methods provided by the tape library vendors. Within three hours, the libraries were back up scanning the tapes and performing thousands of restore jobs onto distributed compute storage.
當卡車還在路上時，資料中心技術人員將幾個磁帶櫃停機進行維護，並移除了數千卷磁帶，以便為大規模的資料恢復操作騰出空間。然後，當數千卷磁帶在凌晨時分抵達時，技術人員開始辛苦地用手裝載磁帶。在過去的 DiRT 演習中，這種手動過程被證明比磁帶櫃供應商提供的基於機器人的方法，在進行大規模恢復時快上數百倍。在三小時內，磁帶櫃重新上線，掃描磁帶並將數千個恢復工作執行到分散式計算儲存上。

Despite the team’s DiRT experience, the massive 1.5 petabyte recovery took longer than the two days estimated. By the morning of March 10th, only 74% of the 436,223 audio files had been successfully transferred from 3,475 recalled backup tapes to distributed filesystem storage at a nearby compute cluster. The other 1,862 backup tapes had been omitted from the tape recall process by a vendor. In addition, the recovery process had been held up by 17 bad tapes. In anticipation of a failure due to bad tapes, a redundant encoding had been used to write the backup files. Additional truck deliveries were set off to recall the redundancy tapes, along with the other 1,862 tapes that had been omitted by the first offsite recall.
儘管團隊有 DiRT 經驗，但這次 massive 1.5 petabyte 的恢復時間比預計的兩天要長。到 3 月 10 日早上，只有 74% 的 436,223 個音訊檔案成功地從 3,475 個召回的備份磁帶轉移到附近計算叢集的分散式檔案系統儲存中。另外 1,862 個備份磁帶被供應商在磁帶召回過程中遺漏了。此外，恢復過程還被 17 個壞磁帶耽擱了。為了預防因壞磁帶導致的故障，備份檔案寫入時使用了冗餘編碼。額外的卡車運輸被安排去召回冗餘磁帶，以及第一次異地召回中被遺漏的另外 1,862 個磁帶。

By the morning of March 11th, over 99.95% of the restore operation had completed, and the recall of additional redundancy tapes for the remaining files was in progress. Although the data was safely on distributed filesystems, additional data recovery steps were necessary in order to make them accessible to users. The Google Music Team began exercising these final steps of the data recovery process in parallel on a small sample of recovered audio files to make sure the process still worked as expected.
到 3 月 11 日早上，超過 99.95% 的恢復操作已經完成，其餘檔案的額外冗餘磁帶召回工作正在進行中。雖然資料已安全地存放在分散式檔案系統上，但仍需要額外的資料恢復步驟才能讓使用者存取。Google Music 團隊開始在一個小的恢復音訊檔案樣本上並行地執行這些最後的資料恢復步驟，以確保該過程仍然如預期般運作。

At that moment, Google Music production pagers sounded due to an unrelated but critical user-affecting production failure a failure that fully engaged the Google Music team for two days. The data recovery effort resumed on March 13th, when all 436,223 audio tracks were once again made accessible to their users. In just short of 7 days, 1.5 petabytes of audio data had been reinstated to users with the help of offsite tape backups; 5 of the 7 days comprised the actual data recovery effort.
就在那時，Google Music 生產環境的呼叫器因為一個不相關但嚴重影響使用者的生產故障而響起——這個故障讓 Google Music 團隊整整忙了兩天。資料恢復工作於 3 月 13 日恢復，屆時所有 436,223 個音軌再次對其使用者開放。在不到 7 天的時間裡，借助異地磁帶備份，1.5 PB 的音訊資料被恢復給使用者；其中 5 天是實際的資料恢復工作。

With the first wave of the recovery process behind them, the team shifted its focus to the other 161,000 missing audio files that had been deleted by the bug before they were backed up. The majority of these files were store-bought and promotional tracks, and the original store copies were unaffected by the bug. Such tracks were quickly reinstated so that the affected users could enjoy their music again.
隨著第一波恢復過程的結束，團隊將焦點轉移到另外 161,000 個在被備份前就被錯誤刪除的遺失音訊檔案。這些檔案中的大多數是商店購買和促銷的曲目，原始的商店副本沒有受到錯誤的影響。這些曲目很快被恢復，以便受影響的使用者可以再次欣賞他們的音樂。

However, a small portion of the 161,000 audio files had been uploaded by the users themselves. The Google Music Team prompted their servers to request that the Google Music clients of affected users re-upload files dating from March 14th onward. This process lasted more than a week. Thus concluded the complete recovery effort for the incident.
然而，在這 161,000 個音訊檔案中，有一小部分是使用者自己上傳的。Google Music 團隊提示他們的伺服器，要求受影響使用者的 Google Music 客戶端重新上傳自 3 月 14 日起的檔案。這個過程持續了一個多星期。至此，該事件的完整恢復工作宣告結束。

### Addressing the root cause
### 解決根本原因

Eventually, the Google Music Team identified the flaw in their refactored data deletion pipeline. To understand this flaw, you first need context about how offline data processing systems evolve on a large scale.
最終，Google Music 團隊確定了他們重構後的資料刪除管道中的缺陷。要理解這個缺陷，你首先需要了解離線資料處理系統在大規模下是如何演變的背景。

For a large and complex service comprising several subsystems and storage services, even a task as simple as removing deleted data needs to be performed in stages, each involving different datastores.
對於一個由多個子系統和儲存服務組成的大型複雜服務來說，即使是像移除已刪除資料這樣簡單的任務，也需要分階段執行，每個階段都涉及不同的資料儲存庫。

For data processing to finish quickly, the processing is parallelized to run across tens of thousands of machines that exert a large load on various subsystems. This distribution can slow the service for users, or cause the service to crash under the heavy load.
為了讓資料處理快速完成，處理過程被並行化，在數以萬計的機器上運行，這會對各種子系統施加巨大的負載。這種分佈可能會減慢為使用者提供的服務，或者導致服務在重負載下崩潰。

To avoid these undesirable scenarios, cloud computing engineers often make a short-lived copy of data on secondary storage, where the data processing is then performed. Unless the relative age of the secondary copies of data is carefully coordinated, this practice introduces race conditions.
為了避免這些不希望出現的情境，雲端運算工程師通常會在次級儲存上製作一個短生命週期的資料副本，然後在那裡進行資料處理。除非次級資料副本的相對年齡經過仔細協調，否則這種做法會引入競爭條件 (race conditions)。

For instance, two stages of a pipeline may be designed to run in strict succession, three hours apart, so that the second stage can make a simplifying assumption about the correctness of its inputs. Without this simplifying assumption, the logic of the second stage may be hard to parallelize. But the stages may take longer to complete as the volume of data grows. Eventually, the original design assumptions may no longer hold for certain pieces of data needed by the second stage.
例如，一個管道的兩個階段可能被設計成嚴格地相繼運行，間隔三小時，這樣第二階段就可以對其輸入的正確性做出一個簡化的假設。如果沒有這個簡化的假設，第二階段的邏輯可能很難並行化。但隨著資料量的增長，這些階段可能需要更長的時間才能完成。最終，原始的設計假設對於第二階段所需的某些資料可能不再成立。

At first, this race condition may occur for a tiny fraction of data. But as the volume of data increases, a larger and larger fraction of the data is at risk for triggering a race condition. Such a scenario is probabilistic the pipeline works correctly for the vast majority of data and for most of the time. When such race conditions occur in a data deletion pipeline, the wrong data can be deleted nondeterministically.
起初，這種競爭條件 (race condition) 可能只發生在極小一部分資料上。但隨著資料量的增加，越來越大的資料比例面臨觸發競爭條件的風險。這種情況是機率性的——管道在絕大多數資料和大部分時間裡都能正常工作。當這種競爭條件發生在資料刪除管道中時，錯誤的資料可能會被非確定性地刪除。

Google Music’s data deletion pipeline was designed with coordination and large margins for error in place. But when upstream stages of the pipeline began to require increased time as the service grew, performance optimizations were put in place so Google Music could continue to meet privacy requirements. As a result, the probability of an inadvertent data-deleting race condition in this pipeline began to increase. When the pipeline was refactored, this probability again significantly increased, up to a point at which the race conditions occurred more regularly.
Google Music 的資料刪除管道在設計時就考慮了協調性和較大的容錯邊際。但隨著服務的增長，管道的上游階段開始需要更長的時間，為了讓 Google Music 能夠繼續滿足隱私要求，我們進行了效能最佳化。結果，這個管道中發生無意中刪除資料的競爭條件 (race condition) 的機率開始增加。當管道被重構時，這個機率再次顯著增加，直到競爭條件更頻繁地發生。

In the wake of the recovery effort, Google Music redesigned its data deletion pipeline to eliminate this type of race condition. In addition, we enhanced production monitoring and alerting systems to detect similar large-scale runaway deletion bugs with the aim of detecting and fixing such issues before users notice any problems. 133
在恢復工作之後，Google Music 重新設計了其資料刪除管道，以消除這種類型的競爭條件 (race condition)。此外，我們增強了生產監控和警報系統，以偵測類似的大規模失控刪除錯誤，目標是在使用者注意到任何問題之前偵測並修復此類問題。133

# General Principles of SRE as Applied to Data Integrity
# SRE 通用原則在資料完整性上的應用

General principles of SRE can be applied to the specifics of data integrity and cloud computing as described in this section.
SRE 的通用原則可以應用於本節所述的資料完整性和雲端運算的具體細節。

## Beginner’s Mind
## 初學者之心

Large-scale, complex services have inherent bugs that can’t be fully grokked. Never think you understand enough of a complex system to say it won’t fail in a certain way. Trust but verify, and apply defense in depth. (Note: "Beginner’s mind" does not suggest putting a new hire in charge of that data deletion pipeline!)
大規模、複雜的服務存在固有的錯誤，無法被完全理解。永遠不要認為你對一個複雜系統的了解足以斷言它不會以某種方式失敗。信任但要驗證，並應用深度防禦 (defense in depth)。（注意：「初學者之心」並不是建議讓一個新進員工負責那個資料刪除管道！）

## Trust but Verify
## 信任但要驗證

Any API upon which you depend won’t work perfectly all of the time. It’s a given that regardless of your engineering quality or rigor of testing, the API will have defects. Check the correctness of the most critical elements of your data using out-of-band data validators, even if API semantics suggest that you need not do so. Perfect algorithms may not have perfect implementations.
你所依賴的任何 API 都不會一直完美運作。這是一個既定事實，無論你的工程品質或測試嚴謹度如何，API 都會有缺陷。使用帶外 (out-of-band) 資料驗證器檢查你資料中最關鍵元素的正確性，即使 API 語義建議你不需要這樣做。完美的演算法可能沒有完美的實作。

## Hope Is Not a Strategy
## 希望不是一種策略

System components that aren’t continually exercised fail when you need them most. Prove that data recovery works with regular exercise, or data recovery won’t work. Humans lack discipline to continually exercise system components, so automation is your friend. However, when you staff such automation efforts with engineers who have competing priorities, you may end up with temporary stopgaps.
沒有持續演練的系統元件，在你最需要它們的時候會失敗。透過定期演練來證明資料恢復是可行的，否則資料恢復就行不通。人類缺乏持續演練系統元件的紀律，所以自動化是你的朋友。然而，當你讓有競爭優先順序的工程師來負責這些自動化工作時，你最終可能只會得到臨時的權宜之計。

## Defense in Depth
## 深度防禦 (Defense in Depth)

Even the most bulletproof system is susceptible to bugs and operator error. In order for data integrity issues to be fixable, services must detect such issues quickly. Every strategy eventually fails in changing environments. The best data integrity strategies are multitiered multiple strategies that fall back to one another and address a broad swath of scenarios together at reasonable cost.
即使是最堅不可摧的系統也容易受到錯誤和操作員失誤的影響。為了使資料完整性問題能夠被修復，服務必須迅速偵測到此類問題。每種策略在不斷變化的環境中最終都會失敗。最好的資料完整性策略是多層次的——多種策略相互備援，並以合理的成本共同應對廣泛的情境。

The fact that your data “was safe yesterday” isn’t going to help you tomorrow, or even today. Systems and infrastructure change, and you’ve got to prove that your assumptions and processes remain relevant in the face of progress. Consider the following.
你的資料「昨天是安全的」這個事實，對明天甚至今天都沒有幫助。系統和基礎設施會改變，你必須證明你的假設和流程在進步面前仍然是相關的。考慮以下情況。

The Shakespeare service has received quite a bit of positive press, and its user base is steadily increasing. No real attention was paid to data integrity as the service was being built. Of course, we don’t want to serve bad bits, but if the index Bigtable is lost, we can easily re-create it from the original Shakespeare texts and a MapReduce. Doing so would take very little time, so we never made backups of the index.
莎士比亞服務獲得了相當多的正面報導，其使用者基礎也在穩步增長。在建立服務時，並沒有真正關注資料完整性。當然，我們不想提供壞的位元，但如果索引 Bigtable 遺失了，我們可以輕易地從原始的莎士比亞文本和一個 MapReduce 中重新創建它。這樣做花費的時間很少，所以我們從來沒有備份過索引。

Now a new feature allows users to make text annotations. Suddenly, our dataset can no longer be easily re-created, while the user data is increasingly valuable to our users. Therefore, we need to revisit our replication options we’re not just replicating for latency and bandwidth, but for data integrity, as well. Therefore, we need to create and test a backup and restore procedure. This procedure is also periodically tested by a DiRT exercise to ensure that we can restore users’ annotations from backups within the time set by the SLO.
現在一個新功能允許使用者進行文字註釋。突然之間，我們的資料集不再能輕易地重新創建，而使用者資料對我們的使用者來說也越來越有價值。因此，我們需要重新審視我們的複製 (replication) 選項——我們不僅僅是為了延遲和頻寬而複製，也是為了資料完整性。因此，我們需要建立並測試一個備份和還原程序。這個程序也由 DiRT 演習定期測試，以確保我們可以在 SLO 設定的時間內從備份中還原使用者的註釋。

# Conclusion
# 結論

Data availability must be a foremost concern of any data-centric system. Rather than focusing on the means to the end, Google SRE finds it useful to borrow a page from test-driven development by proving that our systems can maintain data availability with a predicted maximum down time. The means and mechanisms that we use to achieve this end goal are necessary evils. By keeping our eyes on the goal, we avoid falling into the trap in which "The operation was a success, but the system died."
資料可用性必須是任何以資料為中心的系統的首要考量。Google SRE 發現，與其專注於達成目的的手段，不如借鏡測試驅動開發 (test-driven development) 的一頁，透過證明我們的系統能夠在預測的最大停機時間內維持資料可用性。我們用來達成這個最終目標的手段和機制是必要的惡。透過專注於目標，我們避免陷入「手術成功了，但系統死了」的陷阱。

Recognizing that not just anything can go wrong, but that everything will go wrong is a significant step toward preparation for any real emergency. A matrix of all possible combinations of disasters with plans to address each of these disasters permits you to sleep soundly for at least one night; keeping your recovery plans current and exercised permits you to sleep the other 364 nights of the year.
認識到不僅僅是任何事情都可能出錯，而是所有事情都會出錯，是為任何真正緊急情況做準備的重要一步。一個包含所有可能災難組合的矩陣，並附有應對每種災難的計畫，能讓你至少安睡一晚；而讓你的恢復計畫保持最新並經過演練，則能讓你安睡一年中的另外 364 個夜晚。

As you get better at recovering from any breakage in reasonable time N , find ways to whittle down that time through more rapid and finer-grained loss detection, with the goal of approaching N = 0 . You can then switch from planning recovery to planning prevention, with the aim of achieving the holy grail of all the data, all the time . Achieve this goal, and you can sleep on the beach on that well-deserved vacation.
當你越來越擅長在合理的時間 N 內從任何損壞中恢復時，就要想辦法透過更快速、更精細的損失偵測來縮短那個時間，目標是接近 N = 0。然後你可以從規劃恢復轉向規劃預防，目標是達到「所有資料，隨時可用」的聖杯。實現這個目標，你就可以在那個應得的假期裡，在沙灘上安睡了。

122 Atomicity, Consistency, Isolation, Durability; see https://en.wikipedia.org/wiki/ACID . SQL databases such as MySQL and PostgreSQL strive to achieve these properties.
122 原子性 (Atomicity)、一致性 (Consistency)、隔離性 (Isolation)、持久性 (Durability)；請參閱 https://en.wikipedia.org/wiki/ACID。像 MySQL 和 PostgreSQL 這樣的 SQL 資料庫都力求達到這些特性。

123 Basically Available, Soft state, Eventual consistency; see https://en.wikipedia.org/wiki/Eventual_consistency . BASE systems, like Bigtable and Megastore, are often also described as "NoSQL."
123 基本可用 (Basically Available)、軟狀態 (Soft state)、最終一致性 (Eventual consistency)；請參閱 https://en.wikipedia.org/wiki/Eventual_consistency。像 Bigtable 和 Megastore 這樣的 BASE 系統，通常也被描述為 "NoSQL"。

124 For further reading on ACID and BASE APIs, see [Gol14] and [Bai13] .
124 關於 ACID 和 BASE API 的進一步閱讀，請參閱 [Gol14] 和 [Bai13]。

125 Binary Large Object; see https://en.wikipedia.org/wiki/Binary_large_object .
125 二進位大型物件 (Binary Large Object)；請參閱 https://en.wikipedia.org/wiki/Binary_large_object。

126 See https://en.wikipedia.org/wiki/Zero-day_(computing) .
126 請參閱 https://en.wikipedia.org/wiki/Zero-day_(computing)。

127 Clay tablets are the oldest known examples of writing. For a broader discussion of preserving data for the long haul, see [Con96] .
127 泥板是已知最古老的書寫範例。關於長期保存資料的更廣泛討論，請參閱 [Con96]。

128 Upon reading this advice, one might ask: since you have to offer an API on top of the datastore to implement soft deletion, why stop at soft deletion, when you could offer many other features that protect against accidental data deletion by users? To take a specific example from Google’s experience, consider Blobstore: rather than allow customers to delete Blob data and metadata directly, the Blob APIs implement many safety features, including default backup policies (offline replicas), end-to-end checksums, and default tombstone lifetimes (soft deletion). It turns out that on multiple occasions, soft deletion saved Blobstore’s clients from data loss that could have been much, much worse. There are certainly many deletion protection features worth calling out, but for companies with required data deletion deadlines, soft deletion was the most pertinent protection against bugs and accidental deletion in the case of Blobstore’s clients.
128 讀到這個建議後，有人可能會問：既然你必須在資料儲存庫之上提供一個 API 來實作軟刪除 (soft deletion)，為什麼只停留在軟刪除，而不提供許多其他可以保護使用者免於意外刪除資料的功能呢？以 Google 的經驗為具體例子，考慮 Blobstore：Blob API 並不允許客戶直接刪除 Blob 資料和元資料，而是實作了許多安全功能，包括預設備份政策（離線複本）、端到端校驗和，以及預設的墓碑生命週期（軟刪除）。事實證明，在多次情況下，軟刪除都從可能更嚴重的資料遺失中拯救了 Blobstore 的客戶。當然還有許多值得一提的刪除保護功能，但對於有資料刪除期限要求的公司來說，在 Blobstore 客戶的案例中，軟刪除是對抗錯誤和意外刪除最為切題的保護措施。

129 "Snapshot" here refers to a read-only, static view of a storage instance, such as snapshots of SQL databases. Snapshots are often implemented using copy-on-write semantics for storage efficiency. They can be expensive for two reasons: first, they contend for the same storage capacity as the live datastores, and second, the faster your data mutates, the less efficiency is gained from copying-on-write.
129 這裡的「快照 (Snapshot)」指的是儲存實例的一個唯讀、靜態的視圖，例如 SQL 資料庫的快照。快照通常使用寫入時複製 (copy-on-write) 的語義來實現儲存效率。它們可能很昂貴有兩個原因：首先，它們與即時資料儲存庫競爭相同的儲存容量；其次，你的資料變化越快，從寫入時複製中獲得的效率就越低。

130 For more information on GFS-style replication, see [Ghe03] . For more information on Reed-Solomon erasure codes, see https://en.wikipedia.org/wiki/Reed–Solomon_error_correction .
130 關於 GFS 風格的複製 (replication) 的更多資訊，請參閱 [Ghe03]。關於里德-所羅門糾刪碼 (Reed-Solomon erasure codes) 的更多資訊，請參閱 https://en.wikipedia.org/wiki/Reed–Solomon_error_correction。

131 See https://en.wikipedia.org/wiki/Catch-22_(logic) .
131 請參閱 https://en.wikipedia.org/wiki/Catch-22_(logic)。

132 In practice, coming up with a programmatic solution was not a hurdle because the majority of SREs are experienced software engineers, as was the case here. The expectation of such experience makes SREs notoriously hard to find and hire, and from this case study and other data points, you can begin to appreciate why SRE hires practicing software engineers; see [Jon15] .
132 在實務上，想出一個程式化的解決方案並不是一個障礙，因為大多數 SRE 都是經驗豐富的軟體工程師，本案也是如此。這種經驗的期望使得 SRE 非常難找和難以聘用，從這個案例研究和其他資料點，你可以開始理解為什麼 SRE 會聘用執業的軟體工程師；請參閱 [Jon15]。

133 In our experience, cloud computing engineers are often reluctant to set up production alerts on data deletion rates due to natural variation of per-user data deletion rates with time. However, since the intent of such an alert is to detect global rather than local deletion rate anomalies, it would be more useful to alert when the global data deletion rate, aggregated across all users, crosses an extreme threshold (such as 10x the observed 95th percentile), as opposed to less useful per-user deletion rate alerts.
133 根據我們的經驗，雲端運算工程師通常不願意針對資料刪除率設定生產警報，因為每個使用者的資料刪除率會隨著時間自然變化。然而，由於這類警報的目的是偵測全域而非本地的刪除率異常，因此當所有使用者匯總的全域資料刪除率超過一個極端閾值（例如觀測到的第 95 百分位數的 10 倍）時發出警報會更有用，而不是較無用的個別使用者刪除率警報。
