import React from 'react';
import { Share2, Eye, Link as LinkIcon, Wand2, Check } from 'lucide-react';
import { UserProfile } from '../types';

interface ProfileEditorProps {
  formData: UserProfile;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onGenerate: () => void;
  shareLink: string;
  isCopied: boolean;
  onCopy: () => void;
  onPreview: () => void;
}

export const ProfileEditor: React.FC<ProfileEditorProps> = ({
  formData,
  onChange,
  onGenerate,
  shareLink,
  isCopied,
  onCopy,
  onPreview
}) => {
  return (
    <>
      <h2 className="text-2xl font-hand font-bold text-gray-800 mb-4 flex items-center gap-2">
        <Wand2 className="text-primary" /> Thiết kế trang
      </h2>
      <p className="text-sm text-gray-600 mb-6">Nhập thông tin bên dưới, trang sẽ tự cập nhật.</p>

      <div className="space-y-4">
        <div className="space-y-1">
          <label className="text-xs font-bold text-gray-500 uppercase">Tên của bạn</label>
          <input 
            type="text" name="name" value={formData.name} onChange={onChange}
            className="w-full px-4 py-2 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition"
            placeholder="Ví dụ: Nguyễn Văn A"
          />
        </div>

         <div className="space-y-1">
          <label className="text-xs font-bold text-gray-500 uppercase">Câu Slogan "Than nghèo"</label>
          <input 
            type="text" name="slogan" value={formData.slogan} onChange={onChange}
            className="w-full px-4 py-2 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition"
            placeholder="Một câu quote hài hước..."
          />
        </div>

        <div className="space-y-1">
          <label className="text-xs font-bold text-gray-500 uppercase">Avatar URL</label>
          <input 
            type="text" name="avatarUrl" value={formData.avatarUrl} onChange={onChange}
            className="w-full px-4 py-2 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition"
            placeholder="Link ảnh đại diện"
          />
        </div>

        <div className="space-y-1">
          <label className="text-xs font-bold text-gray-500 uppercase">Tên Ngân Hàng</label>
          <input 
            type="text" name="bankName" value={formData.bankName} onChange={onChange}
            className="w-full px-4 py-2 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition"
            placeholder="Techcombank, VCB..."
          />
        </div>

        <div className="space-y-1">
          <label className="text-xs font-bold text-gray-500 uppercase">Số Tài Khoản</label>
          <input 
            type="text" name="bankAccount" value={formData.bankAccount} onChange={onChange}
            className="w-full px-4 py-2 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition"
            placeholder="1234..."
          />
        </div>

        <div className="space-y-1">
          <label className="text-xs font-bold text-gray-500 uppercase">Ví Điện Tử (Tên)</label>
          <input 
            type="text" name="walletName" value={formData.walletName} onChange={onChange}
            className="w-full px-4 py-2 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition"
            placeholder="Momo, ZaloPay..."
          />
        </div>

        <div className="space-y-1">
          <label className="text-xs font-bold text-gray-500 uppercase">Số Ví Điện Tử</label>
          <input 
            type="text" name="walletAccount" value={formData.walletAccount} onChange={onChange}
            className="w-full px-4 py-2 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition"
            placeholder="09xx..."
          />
        </div>

        <div className="space-y-1">
          <label className="text-xs font-bold text-gray-500 uppercase">Link QR Code</label>
          <input 
            type="text" name="qrCodeUrl" value={formData.qrCodeUrl} onChange={onChange}
            className="w-full px-4 py-2 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition"
            placeholder="https://..."
          />
          <p className="text-[10px] text-gray-500">Dùng vietqr.io để tạo link QR đẹp nhé!</p>
        </div>

        <div className="pt-4 border-t border-gray-200/50">
           <button 
              onClick={onGenerate}
              className="w-full bg-gradient-to-r from-primary to-accent text-white font-bold py-3 rounded-xl shadow-lg hover:shadow-xl hover:scale-[1.02] transition-all flex items-center justify-center gap-2 mb-3"
           >
              <LinkIcon size={18} /> Tạo Link Chia Sẻ
           </button>

           {shareLink && (
               <div className="bg-white/50 p-3 rounded-xl border border-white">
                  <p className="text-xs font-bold text-gray-500 mb-1">Link của bạn:</p>
                  <div className="flex gap-2">
                      <input 
                          readOnly 
                          value={shareLink} 
                          className="bg-white w-full text-xs p-2 rounded border border-gray-200 text-gray-600"
                      />
                      <button 
                          onClick={onCopy}
                          className={`p-2 rounded text-white transition-colors ${isCopied ? 'bg-green-500' : 'bg-gray-800'}`}
                      >
                          {isCopied ? <Check size={16} /> : <Share2 size={16} />}
                      </button>
                       <button 
                          onClick={onPreview}
                          className="p-2 bg-blue-500 rounded text-white hover:bg-blue-600 transition-colors"
                          title="Xem trang thực tế"
                      >
                          <Eye size={16} />
                      </button>
                  </div>
               </div>
           )}
        </div>
      </div>
    </>
  );
};