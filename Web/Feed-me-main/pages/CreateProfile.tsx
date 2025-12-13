import React, { useState } from 'react';
import { UserProfile, DEFAULT_PROFILE } from '../types';
import { encodeProfileData } from '../utils';
import { ViewProfile } from './ViewProfile';
import { ProfileEditor } from '../components/ProfileEditor';
import { Wand2, X } from 'lucide-react';

export const CreateProfile: React.FC = () => {
  const [formData, setFormData] = useState<UserProfile>(DEFAULT_PROFILE);
  const [shareLink, setShareLink] = useState('');
  const [isCopied, setIsCopied] = useState(false);
  const [isMobileModalOpen, setIsMobileModalOpen] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleGenerateLink = () => {
    const encoded = encodeProfileData(formData);
    const url = `${window.location.origin}${window.location.pathname}#/view?data=${encoded}`;
    setShareLink(url);
    setIsCopied(false);
  };

  const copyLink = () => {
    if(!shareLink) return;
    navigator.clipboard.writeText(shareLink).then(() => {
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2500);
    });
  };

  const previewInNewTab = () => {
     if(shareLink) {
         window.open(shareLink, '_blank');
     } else {
        const encoded = encodeProfileData(formData);
        const url = `${window.location.origin}${window.location.pathname}#/view?data=${encoded}`;
        window.open(url, '_blank');
     }
  }

  const defaultStory = `## 🎮 Lý do thực hiện

T1 đến Việt Nam – đây là cơ hội hiếm có trong đời! Là một fan trung thành của T1 và eSports, tôi muốn được gặp trực tiếp các tuyển thủ huyền thoại.

## 🎯 Mục tiêu

- ✅ Có đủ kinh phí để đi xem T1 tại Việt Nam
- ✅ Ghi lại toàn bộ hành trình bằng hình ảnh và video
- ✅ Lan tỏa tinh thần yêu T1 và cộng đồng eSports Việt Nam

## 💝 Ý nghĩa

Đây không chỉ là về tiền bạc, mà là động lực và sự ủng hộ tinh thần từ cộng đồng. Mỗi đóng góp nhỏ đều giúp tôi thêm một bước gần hơn đến ước mơ!

## 📋 Kế hoạch chi tiết

**Chi phí dự kiến:**
- 🎫 Vé sự kiện: 2.000.000 VND
- 🚗 Di chuyển (vé máy bay/xe): 3.000.000 VND
- 🏨 Ăn ở: 2.000.000 VND
- 📸 Thiết bị ghi hình: 3.000.000 VND

**Tổng: 10.000.000 VND**

## 🤝 Cam kết

✨ **Minh bạch 100%**: Công khai toàn bộ chi phí và cách sử dụng
📸 **Chia sẻ trải nghiệm**: Hình ảnh, video, cảm nhận sau sự kiện
🎬 **Làm nội dung**: Review, vlog về hành trình gặp T1
💌 **Tri ân**: Cảm ơn tất cả những người ủng hộ

---

*Cảm ơn bạn đã tin tưởng và ủng hộ! T1 Fighting! 🔥*`;

  // Thêm interface cho budget breakdown
  interface BudgetItem {
    label: string;
    percentage: number;
    color: string;
  }

  const budgetBreakdown: BudgetItem[] = [
    { label: "Ăn uống", percentage: 50, color: "#ff6b6b" },
    { label: "Điện nước Internet", percentage: 20, color: "#4ecdc4" },
    { label: "Thuê nhà", percentage: 15, color: "#ffe66d" },
    { label: "Y tế", percentage: 10, color: "#95b8ff" },
    { label: "Học tập", percentage: 10, color: "#a78bfa" },
    { label: "Giải trí", percentage: 5, color: "#ff8ba7" }
  ];

  // Component hiển thị budget breakdown
  const BudgetBreakdown = () => {
    return (
      <div style={{
        background: 'linear-gradient(135deg, #ffc2e2 0%, #ffd4e8 100%)',
        padding: '2rem',
        borderRadius: '1rem',
        marginTop: '2rem'
      }}>
        <h2 style={{
          textAlign: 'center',
          color: '#e63946',
          fontSize: '1.5rem',
          marginBottom: '1.5rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '0.5rem'
        }}>
          🧾 TIỀN BAY ĐI ĐÂU?
        </h2>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {budgetBreakdown.map((item, index) => (
            <div key={index} style={{ marginBottom: '0.5rem' }}>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginBottom: '0.5rem',
                color: '#333',
                fontWeight: '500'
              }}>
                <span>{item.label}</span>
                <span>{item.percentage}%</span>
              </div>
              <div style={{
                width: '100%',
                height: '10px',
                background: '#fff',
                borderRadius: '10px',
                overflow: 'hidden'
              }}>
                <div style={{
                  width: `${item.percentage}%`,
                  height: '100%',
                  background: item.color,
                  borderRadius: '10px',
                  transition: 'width 0.3s ease'
                }} />
              </div>
            </div>
          ))}
        </div>
        
        <p style={{
          textAlign: 'center',
          marginTop: '1.5rem',
          fontSize: '0.875rem',
          color: '#666',
          fontStyle: 'italic'
        }}>
          *Biểu đồ cập nhật hằng tuần (hứa danh dự)!
        </p>
      </div>
    );
  };

  return (
    <div className="flex flex-col lg:flex-row gap-8 max-w-7xl mx-auto items-start relative">
      
      {/* Desktop Editor - Sidebar (Hidden on mobile) */}
      <div className="hidden lg:block w-1/3 glass-panel p-6 rounded-2xl sticky top-8 max-h-[90vh] overflow-y-auto">
        <ProfileEditor 
            formData={formData} 
            onChange={handleInputChange} 
            onGenerate={handleGenerateLink}
            shareLink={shareLink}
            isCopied={isCopied}
            onCopy={copyLink}
            onPreview={previewInNewTab}
        />
      </div>

      {/* Mobile FAB (Visible only on mobile) */}
      <button 
        onClick={() => setIsMobileModalOpen(true)}
        className="lg:hidden fixed bottom-6 right-6 z-50 bg-gradient-to-r from-primary to-accent text-white p-4 rounded-full shadow-2xl hover:scale-110 transition-transform flex items-center justify-center animate-bounce"
        aria-label="Chỉnh sửa thông tin"
        style={{ animationDuration: '2s' }}
      >
        <Wand2 size={28} />
      </button>

      {/* Mobile Modal */}
      {isMobileModalOpen && (
        <div className="fixed inset-0 z-[100] flex items-end sm:items-center justify-center bg-black/60 backdrop-blur-sm p-0 sm:p-4 animate-[fadeIn_0.2s_ease-out]">
          <div className="bg-white/95 backdrop-blur-md w-full h-[85vh] sm:h-auto sm:max-w-lg rounded-t-3xl sm:rounded-3xl shadow-2xl flex flex-col overflow-hidden animate-[slideUp_0.3s_ease-out]">
             
             {/* Modal Header */}
             <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-white/50">
                <h3 className="font-bold text-lg text-gray-800 flex items-center gap-2">
                    <Wand2 size={18} className="text-primary"/> Chỉnh sửa thông tin
                </h3>
                <button 
                    onClick={() => setIsMobileModalOpen(false)}
                    className="p-2 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors text-gray-600"
                >
                    <X size={20} />
                </button>
             </div>

             {/* Modal Content */}
             <div className="p-6 overflow-y-auto flex-1 pb-20 sm:pb-6">
                <ProfileEditor 
                    formData={formData} 
                    onChange={handleInputChange} 
                    onGenerate={handleGenerateLink}
                    shareLink={shareLink}
                    isCopied={isCopied}
                    onCopy={copyLink}
                    onPreview={previewInNewTab}
                />
             </div>
          </div>
        </div>
      )}

      {/* Preview Column */}
      <div className="w-full lg:w-2/3 mx-auto">
         {/* Mobile view now has full width preview */}
         <div className="opacity-100 transition-opacity duration-500 pb-24 lg:pb-0">
            <ViewProfile data={formData} isPreview={true} />
         </div>
      </div>

      {/* Inline styles for custom animations if not in Tailwind config */}
      <style>{`
        @keyframes slideUp {
          from { transform: translateY(100%); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
      `}</style>

      {/* Budget Breakdown Component */}
      <BudgetBreakdown />
    </div>
  );
};