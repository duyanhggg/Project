import React, { useState } from 'react';
import { UserProfile } from '../types';
import { Toast } from '../components/Toast';
import { 
  TrendingUp, 
  Search, 
  PiggyBank, 
  Smartphone, 
  Sun, 
  FileText, 
  Barcode, 
  Video, 
  Headphones, 
  MessageCircle, 
  Check, 
  X,
  CreditCard,
  Wallet,
  Copy,
  Edit2,
  Image
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { url } from 'inspector';

interface ViewProfileProps {
  data: UserProfile;
  isPreview?: boolean;
}

export const ViewProfile: React.FC<ViewProfileProps> = ({ data, isPreview = false }) => {
  const [toastMsg, setToastMsg] = useState('');
  const [showToast, setShowToast] = useState(false);

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text).then(() => {
      setToastMsg(`Đã copy ${label}: ${text}`);
      setShowToast(true);
    });
  };

  // Thêm danh sách ảnh T1
  const t1Images = [
    { url: 'https://cdn2.fptshop.com.vn/unsafe/800x0/doi_hinh_t1_lol_2025_1_b157097804.jpg', caption: 'T1 Team 2025' },
    { url: 'https://scontent.fhan3-5.fna.fbcdn.net/v/t39.30808-6/506351228_1154697593367655_5035815365336975291_n.jpg?_nc_cat=108&ccb=1-7&_nc_sid=833d8c&_nc_eui2=AeEyb-d5jh3xtOsZoZyV49JzhZvXSKsp27qFm9dIqynbupt9gp0wY5EsJHV-79n7jqVwp_sG9tNL4r1pfBn5hOTG&_nc_ohc=L2nOMJNnCUQQ7kNvwElsx6O&_nc_oc=AdkiGP9nRFV47UMnaFSXAsyVofajdLEXpjdmM0AR9TbykGmvCC7wT7zfFOq8Ei3N-5Flal4IIGamDCmZjxB9lKDX&_nc_zt=23&_nc_ht=scontent.fhan3-5.fna&_nc_gid=a2HL6Rw-Y27ZywErpoFi5g&oh=00_AflvMFLcbjU-JdPuWtviQsFFOAmG0ae1_q8daJ0O5i4QZg&oe=6941EDFB', caption: 'Faker - GOAT' },
    { url: 'data:image/jpeg;base64,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', caption: 'T1 at Worlds' },
    { url: 'https://cafefcdn.com/thumb_w/640/203337114487263232/2025/12/6/photo1765002575453-1765002575749588981854-1765003518830112687538.jpg', caption: 'T1 Coming to Vietnam' }
  ];

  return (
    <div className="w-full max-w-2xl mx-auto glass-panel rounded-[24px] overflow-hidden relative shadow-2xl animate-fade-in-up">
      {/* Edit Button if viewing own profile context or just accessible */}
      {!isPreview && (
        <Link to="/" className="absolute top-4 right-4 bg-white/40 hover:bg-white/80 p-2 rounded-full transition-colors z-10 text-white" title="Tạo trang của bạn">
           <Edit2 size={20} />
        </Link>
      )}

      {/* Header */}
      <div className="bg-gradient-to-r from-[#ff758c] to-[#ff7eb3] p-8 text-center text-white">
        <div className="relative inline-block">
          <img 
            src={data.avatarUrl} 
            alt="Avatar" 
            className="w-28 h-28 rounded-full border-4 border-white/80 bg-white object-cover mx-auto mb-4 shadow-lg"
            onError={(e) => { (e.target as HTMLImageElement).src = 'https://api.dicebear.com/7.x/fun-emoji/svg?seed=Fallback'; }}
          />
        </div>
        <h1 className="font-hand text-4xl md:text-5xl mb-2 drop-shadow-md">
          NUÔI {data.name.toUpperCase()} ĐI! 🥺
        </h1>
        <p className="text-lg italic opacity-90 font-medium">
          {data.slogan}
        </p>
      </div>

      <div className="p-6 md:p-8 space-y-8">
        
        {/* T1 Gallery Section - THÊM MỚI */}
        <section>
          <div className="text-center mb-6">
            <h2 className="text-[#d63031] font-extrabold text-xl uppercase tracking-wider inline-block relative pb-2 after:content-[''] after:absolute after:bottom-0 after:left-1/2 after:-translate-x-1/2 after:w-12 after:h-1 after:bg-[#d63031] after:rounded-full flex items-center gap-2 justify-center">
              <Image size={24} />
              🏆 T1 - 5 Anh Hề Huyền Thoại
            </h2>
          </div>
          <div className="grid grid-cols-2 gap-4">
            {t1Images.map((img, index) => (
              <div 
                key={index} 
                className="relative group overflow-hidden rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1"
              >
                <img 
                  src={img.url} 
                  alt={img.caption}
                  className="w-full h-48 object-cover transition-transform duration-300 group-hover:scale-110"
                  onError={(e) => { 
                    (e.target as HTMLImageElement).src = `https://placehold.co/400x300/ff758c/white?text=${encodeURIComponent(img.caption)}`; 
                  }}
                />
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-3">
                  <p className="text-white text-sm font-bold text-center">{img.caption}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded-r-lg">
            <p className="text-sm text-yellow-800 font-medium">
              🎮 <strong>Đây là lý do tôi cần được nuôi!</strong> T1 đến Việt Nam là cơ hội hiếm có trong đời. 
              Giúp tôi gặp được 5 anh hề này nhé! 🙏
            </p>
          </div>
        </section>

        {/* Why Feed Me */}
        <section>
          <div className="text-center mb-6">
            <h2 className="text-[#d63031] font-extrabold text-xl uppercase tracking-wider inline-block relative pb-2 after:content-[''] after:absolute after:bottom-0 after:left-1/2 after:-translate-x-1/2 after:w-12 after:h-1 after:bg-[#d63031] after:rounded-full">
              🎯 Tại Sao Nên Nuôi Tôi?
            </h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FeatureBox icon={<TrendingUp size={32} />} title="Sao Kê Realtime" desc="Cập nhật từng giây! Nhanh hơn cả tốc độ bạn chuyển tiền." />
            <FeatureBox icon={<Search size={32} />} title="Minh Bạch 300%" desc="Báo cáo cả việc mua ly trà sữa full topping." />
            <FeatureBox icon={<PiggyBank size={32} />} title="Chi Tiêu Hợp Lý" desc="Không G63. Chỉ mì tôm 2 trứng và trà đá." />
            <FeatureBox icon={<Smartphone size={32} />} title="App Tracking" desc="Theo dõi 24/7 tôi ăn gì, ở đâu như 'Big Brother'." />
          </div>
        </section>

        {/* Golden Commitment */}
        <section>
          <div className="text-center mb-6">
            <h2 className="text-[#d63031] font-extrabold text-xl uppercase tracking-wider inline-block relative pb-2 after:content-[''] after:absolute after:bottom-0 after:left-1/2 after:-translate-x-1/2 after:w-12 after:h-1 after:bg-[#d63031] after:rounded-full">
              🎪 Cam Kết Vàng
            </h2>
          </div>
          <div className="bg-white/50 rounded-2xl p-6 shadow-sm">
            <ListItem icon={<Sun />} text="Sao kê mỗi ngày: Cập nhật lúc 6h sáng, đều như vắt chanh!" />
            <ListItem icon={<FileText />} text="Không giấu giếm: Từ tô phở 50k đến hộp sữa chua 8k." />
            <ListItem icon={<Barcode />} text="Full hóa đơn: Chụp bill, quét mã vạch, lưu biên lai đầy đủ." />
            <ListItem icon={<Video />} text="Video unboxing: Mở từng gói mì tôm live trên Facebook." />
            <ListItem icon={<Headphones />} text="Hotline 24/7: Gọi hỏi tôi ăn gì bất cứ lúc nào." />
            <ListItem icon={<MessageCircle />} text="Không block: Hỏi khó đến mấy cũng trả lời." />
          </div>
        </section>

        {/* Comparison */}
        <section>
          <div className="text-center mb-6">
             <h2 className="text-[#d63031] font-extrabold text-xl uppercase tracking-wider inline-block relative pb-2 after:content-[''] after:absolute after:bottom-0 after:left-1/2 after:-translate-x-1/2 after:w-12 after:h-1 after:bg-[#d63031] after:rounded-full">
              💰 So Sánh Nè
            </h2>
          </div>
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 bg-red-500/10 border border-red-500/20 rounded-xl p-5">
              <h3 className="text-center font-bold text-red-700 uppercase mb-4">Người Khác</h3>
              <ul className="space-y-2 text-sm text-gray-700">
                <li className="flex gap-2"><X className="text-red-500 w-4 h-4 mt-0.5 flex-shrink-0"/> Sao kê sau 3 năm</li>
                <li className="flex gap-2"><X className="text-red-500 w-4 h-4 mt-0.5 flex-shrink-0"/> File Excel mờ tịt</li>
                <li className="flex gap-2"><X className="text-red-500 w-4 h-4 mt-0.5 flex-shrink-0"/> Số liệu "làm tròn"</li>
                <li className="flex gap-2"><X className="text-red-500 w-4 h-4 mt-0.5 flex-shrink-0"/> Hay block người hỏi</li>
              </ul>
            </div>
            <div className="flex-1 bg-green-500/10 border border-green-500/20 rounded-xl p-5">
              <h3 className="text-center font-bold text-green-700 uppercase mb-4">Nuôi Tôi</h3>
              <ul className="space-y-2 text-sm text-gray-700">
                <li className="flex gap-2"><Check className="text-green-600 w-4 h-4 mt-0.5 flex-shrink-0"/> Sao kê TRƯỚC khi tiêu</li>
                <li className="flex gap-2"><Check className="text-green-600 w-4 h-4 mt-0.5 flex-shrink-0"/> File Excel 4K Ultra HD</li>
                <li className="flex gap-2"><Check className="text-green-600 w-4 h-4 mt-0.5 flex-shrink-0"/> Chính xác từng đồng</li>
                <li className="flex gap-2"><Check className="text-green-600 w-4 h-4 mt-0.5 flex-shrink-0"/> Rep inbox siêu tốc</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Spending Plan */}
        <section>
          <div className="text-center mb-6">
            <h2 className="text-[#d63031] font-extrabold text-xl uppercase tracking-wider inline-block relative pb-2 after:content-[''] after:absolute after:bottom-0 after:left-1/2 after:-translate-x-1/2 after:w-12 after:h-1 after:bg-[#d63031] after:rounded-full">
              📈 Tiền Bay Đi Đâu?
            </h2>
          </div>
          <div className="bg-white/50 rounded-2xl p-6 shadow-sm space-y-4">
            <ProgressBar label="Ăn uống" percent={10} color="bg-[#FF6B6B]" />
            <ProgressBar label="Mua vé" percent={60} color="bg-[#4ECDC4]" />
            <ProgressBar label="Đi lại" percent={15} color="bg-[#FFE66D]" />
            <ProgressBar label="Quà Cho Các Mom" percent={15} color="bg-[#95B8FF]" />
            <p className="text-center text-xs text-gray-500 mt-4">*Biểu đồ cập nhật hàng tuần (hứa danh dự)!</p>
          </div>
        </section>

        {/* CTA */}
        <div className="bg-gradient-to-tr from-[#FF512F] to-[#DD2476] rounded-2xl p-8 text-center text-white shadow-xl transform transition hover:scale-[1.01]">
          <h2 className="font-hand text-4xl mb-2">💳 DONATE NGAY ĐI!</h2>
          <p className="text-sm opacity-90 mb-6">(Nếu bạn đã cười khi đọc những dòng trên)</p>
          
          <div className="bg-white p-3 rounded-xl inline-block mb-4 shadow-inner">
            <img 
              src={data.qrCodeUrl} 
              alt="QR Code" 
              className="w-40 h-40 object-contain"
              onError={(e) => { (e.target as HTMLImageElement).src = 'https://placehold.co/150x150?text=No+QR'; }}
            />
          </div>
          <p className="text-xs font-bold mb-6 animate-pulse">⚡ Chuyển xong là có mail tự động! ⚡</p>

          <div className="space-y-3">
            <BankCard 
              icon={<CreditCard size={20} />} 
              name={data.bankName} 
              number={data.bankAccount} 
              onClick={() => copyToClipboard(data.bankAccount, data.bankName)}
            />
             <BankCard 
              icon={<Wallet size={20} />} 
              name={data.walletName} 
              number={data.walletAccount} 
              onClick={() => copyToClipboard(data.walletAccount, data.walletName)}
            />
          </div>
        </div>

        {/* Disclaimer */}
        <div className="mt-8 pt-6 border-t border-gray-200/40 text-center">
            <p className="text-[11px] md:text-xs text-gray-600/80 font-medium italic">
                ⚠️ DISCLAIMER: Đây là trang web mang tính chất HÀI HƯỚC Mọi nội dung đều mang tính giải trí, không nhằm mục đích xúc phạm hay chỉ trích bất kỳ cá nhân/tổ chức nào.
            </p>
        </div>

      </div>

      <Toast 
        message={toastMsg} 
        isVisible={showToast} 
        onClose={() => setShowToast(false)} 
      />
    </div>
  );
};

/* Helper Components */
const FeatureBox = ({ icon, title, desc }: { icon: React.ReactNode, title: string, desc: string }) => (
  <div className="bg-white/60 p-5 rounded-2xl text-center hover:-translate-y-1 transition-transform duration-300 shadow-sm border border-white/40">
    <div className="text-primary flex justify-center mb-3">{icon}</div>
    <h3 className="font-bold text-gray-800 mb-2">{title}</h3>
    <p className="text-sm text-gray-600 leading-snug">{desc}</p>
  </div>
);

const ListItem = ({ icon, text }: { icon: React.ReactNode, text: string }) => (
  <div className="flex items-start gap-3 mb-3 text-sm md:text-base text-gray-700">
    <span className="text-yellow-500 mt-1 flex-shrink-0">{icon}</span>
    <span>{text.split(':').map((part, i) => i === 0 ? <strong key={i}>{part}:</strong> : part)}</span>
  </div>
);

const ProgressBar = ({ label, percent, color }: { label: string, percent: number, color: string }) => (
  <div>
    <div className="flex justify-between text-sm font-bold text-gray-700 mb-1">
      <span>{label}</span>
      <span>{percent}%</span>
    </div>
    <div className="h-3 bg-gray-200/50 rounded-full overflow-hidden">
      <div className={`h-full rounded-full ${color}`} style={{ width: `${percent}%` }}></div>
    </div>
  </div>
);

const BankCard = ({ icon, name, number, onClick }: { icon: React.ReactNode, name: string, number: string, onClick: () => void }) => (
  <button 
    onClick={onClick}
    className="w-full bg-white text-gray-800 p-4 rounded-xl flex items-center justify-between hover:bg-gray-50 transition-colors shadow-lg shadow-black/5 group"
  >
    <div className="flex items-center gap-3 font-bold text-lg">
      <span className="text-primary">{icon}</span>
      <span>{name}</span>
    </div>
    <div className="font-mono bg-gray-100 px-3 py-1 rounded text-base flex items-center gap-2 group-active:scale-95 transition-transform">
      {number}
      <Copy size={14} className="opacity-50" />
    </div>
  </button>
);