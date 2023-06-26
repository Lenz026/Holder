import os
import subprocess
import sys
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication, QFileDialog, QWidget, QVBoxLayout, QHBoxLayout, QAbstractItemView, QPushButton, QLineEdit, QListWidget, QListWidgetItem
os.environ["PATH"] += os.pathsep + "C:/Users/Asus/ffmpeg-master-latest-win64-gpl/bin/"
class otio_export(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)
        self.resize(600, 450)
        top_layout = QHBoxLayout()
        mid_layout = QHBoxLayout()
        bottom_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancel")
        export_btn = QPushButton("Export")
        self.browse_btn = QPushButton("Select file")

        self.line_edit = QLineEdit()
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)

        cancel_btn.clicked.connect(self.close)
        export_btn.clicked.connect(self.export_trigger)
        self.browse_btn.clicked.connect(self.get_file_path)
        
        main_layout.addLayout(top_layout)
        top_layout.addWidget(self.line_edit)
        top_layout.addWidget(self.browse_btn)


        main_layout.addLayout(mid_layout)
        mid_layout.addWidget(self.list_widget)
        

        main_layout.addLayout(bottom_layout)
        bottom_layout.addWidget(cancel_btn)
        bottom_layout.addWidget(export_btn)

    class CheckableWidgetItem(QListWidgetItem):
        def __init__(self, text, list_widget):
            super().__init__(text)
            self.list_widget = list_widget
            self.setFlags(self.flags() | Qt.ItemIsUserCheckable)
            self.setCheckState(Qt.Unchecked)
        def setData(self, role, value):
            super().setData(role, value)
            if role == Qt.CheckStateRole:
                if value == Qt.Checked:
                    self.list_widget.setCurrentItem(self)
                else:
                    self.list_widget.setCurrentItem(None)

    def export_trigger(self,):
        self.export_aaf(self.get_checked_file_paths())
    
    def image_to_mxf(self, input_image, output_mxf=None):
        print(input_image, "MXF-ing")
        print(os.path.basename(input_image).split(".")[0]+".mxf")

        output_folder = "C:/Users/Asus/Desktop/OTIO test/mxf_hold"

        basename = os.path.splitext(os.path.basename(input_image))[0]
        os.makedirs(output_folder, exist_ok=True)

        output_mxf = os.path.join(output_folder, f"{basename}.mxf")
        # output_mxf = f"C:/Users/Asus/Desktop/OTIO TEST/mxf_hold/{os.path.basename(input_image).split('.')[0]+'.mxf'}"


        if not os.path.exists(output_mxf):
            os.makedirs(output_mxf)
        # command = [
        #     "ffmpeg",
        #     "-loop", "1",
        #     "-i", input_image,
        #     "-c:v", "mpeg2video",
        #     "-t", "5",# add ui that allows custom values
        #     "-r", "24",
        #     "-pix_fmt", "yuv420p",
        #     output_mxf
        # ]
        # subprocess.run(command, check=True)
        filename = input_image.split(".")[0]
        output = filename+".mxf"
        subprocess.run(["ffmpeg","-i", input_image, output])
        return output

    def find_mxf_file(self, image_file_name, folder_path=None):
        mxf_file_name = os.path.splitext(image_file_name)[0] + '.mxf'
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file == mxf_file_name:
                    return os.path.join(root, file)
        return None

    def export_aaf(self, files):
        
        from opentimelineio import schema, opentime
        import opentimelineio as otio

        track = otio.schema.Track(kind="Video")

        for image_path in files:
            print(image_path.replace("\\", "\\\\"), "HERE IS A FILE")
            image_path = self.image_to_mxf(image_path.replace("\\", "/"))
            print(image_path,"WTFFFF")
            # self.find_mxf_file()
            # ffmpeg -loop 1 -i input_image.png -c:v mpeg2video -t 5 -r 24 -pix_fmt yuv420p output.mxf
            clip_name = os.path.basename(image_path).split(".")[0]
            media_reference = schema.ExternalReference(target_url=image_path,
                                                       available_range=opentime.TimeRange(
                                                            start_time=opentime.RationalTime(value=0, rate=24),
                                                            duration=opentime.RationalTime(value=1, rate=24)
                                                        )
            )
            print(media_reference, "media ref")
            source_range = opentime.TimeRange(
                start_time=opentime.RationalTime(value=0, rate=24),
                duration=opentime.RationalTime(value=48, rate=24)
            )

            clip = schema.Clip(name=clip_name, media_reference=media_reference, source_range=source_range)
            track.append(clip)
        print(clip, "clip data")
        timeline = otio.schema.Timeline()
        timeline.tracks.append(track)
        otio.adapters.write_to_file(timeline, "example.aaf", adapter_name="AAF",use_empty_mob_ids=True)
        

    def get_checked_file_paths(self):
        base_path = self.line_edit.text()
        checked_item_names = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.Checked:
                checked_item_names.append(item.text())
        file_paths = [os.path.normpath(os.path.join(base_path, name)) for name in checked_item_names]
        return file_paths

    def get_file_path(self,):
        
        file_path = QFileDialog.getExistingDirectory()
        if file_path:
            print(file_path,"###")
            self.line_edit.setText(file_path)
            self.populate_file_view(file_path)
        
    def populate_file_view(self, file_path):

        all_files = []
        self.list_widget.itemChanged.connect(self.on_item_changed)
        for file in os.listdir(file_path):

            if file.endswith((".png", ".jpg", ".PNG", ".JPG", ".JPEG")):
                item = otio_export.CheckableWidgetItem(file, self.list_widget)
                item.setCheckState(Qt.Checked)
                self.list_widget.addItem(item)

                if os.path.isfile(file):
                    all_files.append(file)
            
        all_files

    def on_item_changed(self, item):
        if item.checkState() == Qt.Checked:
            item.setSelected(True)
        else:
            item.setSelected(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = otio_export()
    ex.show()
    sys.exit(app.exec_())

