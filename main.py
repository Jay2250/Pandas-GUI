import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.core.window import Window
import pandas as pd
import matplotlib.pyplot as plt

import io
import contextlib

# Load the .kv file
Builder.load_file('gui.kv')


class PandasApp(BoxLayout):
    df = None  # Placeholder for the dataframe

    def load_data(self):
        # Open file chooser to load a CSV/Excel file
        content = FileChooserIconView(on_submit=self.select_file)
        popup = Popup(title="Open File", content=content, size_hint=(0.9, 0.9))
        popup.open()

    def select_file(self, file_path, *args):
        file_path = file_path.selection[0]  # Get the first selected file
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.df = pd.read_csv(file_path)
                elif file_path.endswith('.xlsx'):
                    self.df = pd.read_excel(file_path)
                self.show_popup("Success", "Data loaded successfully!")
                self.populate_columns()
            except Exception as e:
                self.show_popup("Error", f"Failed to load data: {e}")

    def populate_columns(self):
        if self.df is not None:
            columns = ['None'] + list(self.df.columns)
            self.ids.filter_column.values = columns
            self.ids.group_column.values = columns
            self.ids.x_column.values = self.df.columns
            self.ids.y_column.values = self.df.columns

    def show_head(self):
        if self.df is not None:
            self.display_data(self.df.head(10))

    def show_tail(self):
        if self.df is not None:
            self.display_data(self.df.tail(10))

    def show_sample(self):
        if self.df is not None:
            self.display_data(self.df.sample(10))


    def show_info(self):
        if self.df is not None:
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                self.df.info()  # This writes the output to the buffer instead of stdout
            info_str = buffer.getvalue()
            self.display_data(info_str)  # Send the captured info string to display


    def show_describe(self):
        if self.df is not None:
            _df = self.df.describe().round(2)
            _df.index = ['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']
            self.display_data(_df)



    def show_null_counts(self):
        if self.df is not None:
            null_counts = self.df.isnull().sum()
            null_counts_str = str(null_counts)
            self.show_popup("Null Value Counts", null_counts_str)

    def show_full_data(self):
        if self.df is not None:
            self.display_data(self.df)
    
    def validate_dataframe(self):
        if self.df is None or self.df.empty:
            self.display_message("Error", "No data loaded or the data is empty!")
            return False
        return True

    def apply_filter(self):
        if not self.validate_dataframe():
            return
        if self.df is not None:
            column = self.ids.filter_column.text
            value = self.ids.filter_value.text
            if column and value:
                filtered_df = self.df[self.df[column] == value]
                self.display_data(filtered_df)

    def sort_data(self):
        if self.df is not None:
            sorted_df = self.df.sort_values(by=self.df.columns[0])
            self.display_data(sorted_df)

    def drop_na(self):
        if self.df is not None:
            cleaned_df = self.df.dropna()
            self.display_data(cleaned_df)

    def fill_na(self):
        if self.df is not None:
            filled_df = self.df.fillna(0)  # Filling NA with 0, can be modified
            self.display_data(filled_df)

    def remove_duplicates(self):
        if self.df is not None:
            deduplicated_df = self.df.drop_duplicates()
            self.display_data(deduplicated_df)

    def apply_grouping(self):
        if self.df is not None:
            column = self.ids.group_column.text
            agg_func = self.ids.agg_function.text
            if column and agg_func:
                grouped_df = self.df.groupby(
                    column).agg(agg_func).reset_index()
                self.display_data(grouped_df)

    def plot_data(self):
        if not self.validate_dataframe():
            return
        if self.df is not None:
            plot_type = self.ids.plot_type.text
            x_column = self.ids.x_column.text
            y_column = self.ids.y_column.text
            if plot_type == 'line':
                self.df.plot(x=x_column, y=y_column, kind='line')
            elif plot_type == 'bar':
                self.df.plot(x=x_column, y=y_column, kind='bar')
            elif plot_type == 'hist':
                self.df[y_column].plot(kind='hist')
            elif plot_type == 'scatter':
                self.df.plot(x=x_column, y=y_column, kind='scatter')
            plt.show()

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(
            text=message), size_hint=(0.8, 0.8))
        popup.open()


    def display_data(self, data):
        # Clear previous data
        self.ids.data_grid.clear_widgets()

        if isinstance(data, pd.DataFrame):
            # Add column headers including the first column for index (for describe())
            self.ids.data_grid.add_widget(Label(text="Index", bold=True, size_hint_y=None, height='40dp', size_hint_x=None, width=150))
            for column in data.columns:
                header = Label(text=column, bold=True, size_hint_y=None, height='40dp', size_hint_x=None, width=150)
                self.ids.data_grid.add_widget(header)

            # Add data rows including the index as the first column
            for index, row in data.iterrows():
                self.ids.data_grid.add_widget(Label(text=str(index), size_hint_x=None, width=150, height=40))
                for value in row:
                    button = Button(text=str(value), size_hint_x=None, width=150, height=40)
                    button.bind(on_press=lambda btn, row_index=row: self.on_row_click(row_index))
                    self.ids.data_grid.add_widget(button)

            # Set the number of columns based on DataFrame columns + 1 for index
            self.ids.data_grid.cols = len(data.columns) + 1

        elif isinstance(data, str):
            # Handle string data (already processed info or other text)
            label = Label(text=data, size_hint_y=None, height='40dp', halign='left', valign='top', text_size=(self.width, None))
            label.bind(size=label.setter('text_size'))
            self.ids.data_grid.add_widget(label)

        else:
            # In case of summary statistics like describe(), render them similarly to dataframes
            if isinstance(data, pd.DataFrame):
                data_str = data.to_string()
                label = Label(text=data_str, size_hint_y=None, height='40dp', halign='left', valign='top', text_size=(self.width, None))
                label.bind(size=label.setter('text_size'))
                self.ids.data_grid.add_widget(label)

        # Update layout settings to ensure proper size display in the ScrollView
        self.ids.data_grid.bind(minimum_width=self.ids.data_grid.setter('width'))
        self.ids.data_grid.bind(minimum_height=self.ids.data_grid.setter('height'))

    def on_row_click(self, row_index):
        print(f"Row clicked: {row_index}")  # Debugging print
        # Create a popup to edit the entire row
        edit_popup = Popup(title="Edit Row", size_hint=(0.8, 0.8))
        popup_layout = BoxLayout(orientation='vertical')
    
        # Get the row data
        row_data = self.df.iloc[row_index]
    
        # Create TextInputs for each value in the row
        text_inputs = []
        for col_index, value in enumerate(row_data):
            text_input = TextInput(text=str(value), multiline=False)
            text_inputs.append(text_input)
            popup_layout.add_widget(text_input)
    
        # Create a button to save changes
        save_button = Button(text="Save", size_hint_y=None, height='40dp')
        save_button.bind(on_press=lambda btn: self.save_row_values(
            row_index, text_inputs))
    
        popup_layout.add_widget(save_button)
        edit_popup.content = popup_layout
        edit_popup.open()


    def save_row_values(self, index, text_inputs):
        try:
            # Update the DataFrame with the new values
            for col_index, text_input in enumerate(text_inputs):
                self.df.iat[index, col_index] = float(
                    text_input.text)  # Update value in DataFrame

            self.display_data(self.df)  # Refresh the display
            self.show_popup("Success", "Row updated successfully!")
        except ValueError:
            self.show_popup("Error", "Invalid input! Please enter numeric values.")

    def export_data(self):
        if self.df is not None:
            content = FileChooserIconView(on_submit=self.save_file)
            popup = Popup(title="Save File", content=content,
                          size_hint=(0.9, 0.9))
            popup.open()

    def save_file(self, instance, file_path):
        file_path = file_path[0]
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.df.to_csv(file_path, index=False)
                elif file_path.endswith('.xlsx'):
                    self.df.to_excel(file_path, index=False)
                self.show_popup("Success", "Data exported successfully!")
            except Exception as e:
                self.show_popup("Error", f"Failed to export data: {e}")


class PandasAppMain(App):
    def build(self):
        return PandasApp()


if __name__ == '__main__':
    PandasAppMain().run()
