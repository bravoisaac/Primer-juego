#include "UI/TenFeEquipmentMenuWidget.h"

#include "Blueprint/WidgetTree.h"
#include "Character/TenFeCharacter.h"
#include "Components/Border.h"
#include "Components/Button.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/TenFeEquipmentComponent.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"

namespace
{
    UButton* MakeMenuButton(UWidgetTree* Tree, UVerticalBox* Parent, const FString& Label)
    {
        UButton* Button = Tree->ConstructWidget<UButton>(UButton::StaticClass());
        Button->SetBackgroundColor(FLinearColor(0.16f, 0.18f, 0.22f, 1.0f));

        UTextBlock* Text = Tree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass());
        Text->SetText(FText::FromString(Label));
        Text->SetColorAndOpacity(FSlateColor(FLinearColor::White));
        Text->SetJustification(ETextJustify::Center);
        Button->SetContent(Text);

        Parent->AddChildToVerticalBox(Button)->SetPadding(FMargin(0.0f, 3.0f));
        return Button;
    }
}

void UTenFeEquipmentMenuWidget::SetCharacter(ATenFeCharacter* InCharacter)
{
    Character = InCharacter;
    RefreshSummary();
}

void UTenFeEquipmentMenuWidget::NativeConstruct()
{
    Super::NativeConstruct();
    BuildLayout();
    RefreshSummary();
}

void UTenFeEquipmentMenuWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
    Super::NativeTick(MyGeometry, InDeltaTime);
    RefreshSummary();
}

void UTenFeEquipmentMenuWidget::BuildLayout()
{
    if (WidgetTree->RootWidget)
    {
        return;
    }

    UCanvasPanel* Root = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(), TEXT("MenuRoot"));
    WidgetTree->RootWidget = Root;

    UBorder* Panel = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass(), TEXT("MenuPanel"));
    Panel->SetBrushColor(FLinearColor(0.012f, 0.014f, 0.02f, 0.96f));
    Panel->SetPadding(FMargin(28.0f));
    UCanvasPanelSlot* PanelSlot = Root->AddChildToCanvas(Panel);
    PanelSlot->SetAnchors(FAnchors(0.5f, 0.5f));
    PanelSlot->SetAlignment(FVector2D(0.5f, 0.5f));
    PanelSlot->SetPosition(FVector2D::ZeroVector);
    PanelSlot->SetSize(FVector2D(620.0f, 650.0f));

    UVerticalBox* Stack = WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass(), TEXT("MenuStack"));
    Panel->SetContent(Stack);

    UTextBlock* Title = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass());
    Title->SetText(FText::FromString(TEXT("EQUIPO DEL PEREGRINO")));
    Title->SetJustification(ETextJustify::Center);
    Title->SetColorAndOpacity(FSlateColor(FLinearColor(0.92f, 0.72f, 0.3f)));
    Title->SetFont(FSlateFontInfo(Title->GetFont().FontObject, 28));
    Stack->AddChildToVerticalBox(Title)->SetPadding(FMargin(0.0f, 0.0f, 0.0f, 12.0f));

    SummaryText = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), TEXT("SummaryText"));
    SummaryText->SetJustification(ETextJustify::Center);
    SummaryText->SetColorAndOpacity(FSlateColor(FLinearColor(0.78f, 0.8f, 0.84f)));
    Stack->AddChildToVerticalBox(SummaryText)->SetPadding(FMargin(0.0f, 0.0f, 0.0f, 14.0f));

    AddSectionLabel(Stack, TEXT("ARMAS"));
    UButton* SwordButton = MakeMenuButton(WidgetTree, Stack, TEXT("Espada desgastada  |  Daño 24  |  Peso 4"));
    SwordButton->OnClicked.AddDynamic(this, &UTenFeEquipmentMenuWidget::SelectWeapon0);
    UButton* GreatswordButton = MakeMenuButton(WidgetTree, Stack, TEXT("Mandoble de hierro  |  Daño 38  |  Peso 9"));
    GreatswordButton->OnClicked.AddDynamic(this, &UTenFeEquipmentMenuWidget::SelectWeapon1);
    UButton* SpearButton = MakeMenuButton(WidgetTree, Stack, TEXT("Lanza del cazador  |  Daño 30  |  Peso 6"));
    SpearButton->OnClicked.AddDynamic(this, &UTenFeEquipmentMenuWidget::SelectWeapon2);

    AddSectionLabel(Stack, TEXT("ARMADURA"));
    UButton* HeadButton = MakeMenuButton(WidgetTree, Stack, TEXT("Capucha del peregrino  |  Cabeza  |  Defensa 3"));
    HeadButton->OnClicked.AddDynamic(this, &UTenFeEquipmentMenuWidget::EquipArmor0);
    UButton* ChestButton = MakeMenuButton(WidgetTree, Stack, TEXT("Coraza gastada  |  Pecho  |  Defensa 8"));
    ChestButton->OnClicked.AddDynamic(this, &UTenFeEquipmentMenuWidget::EquipArmor1);
    UButton* LegsButton = MakeMenuButton(WidgetTree, Stack, TEXT("Grebas de hierro  |  Piernas  |  Defensa 5"));
    LegsButton->OnClicked.AddDynamic(this, &UTenFeEquipmentMenuWidget::EquipArmor2);

    UButton* CloseButton = MakeMenuButton(WidgetTree, Stack, TEXT("Cerrar menú  [TAB]"));
    CloseButton->SetBackgroundColor(FLinearColor(0.48f, 0.14f, 0.08f, 1.0f));
    CloseButton->OnClicked.AddDynamic(this, &UTenFeEquipmentMenuWidget::CloseMenu);
}

void UTenFeEquipmentMenuWidget::AddSectionLabel(UVerticalBox* Box, const FString& Label)
{
    UTextBlock* Text = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass());
    Text->SetText(FText::FromString(Label));
    Text->SetColorAndOpacity(FSlateColor(FLinearColor(0.9f, 0.72f, 0.32f)));
    Text->SetFont(FSlateFontInfo(Text->GetFont().FontObject, 18));
    Box->AddChildToVerticalBox(Text)->SetPadding(FMargin(0.0f, 12.0f, 0.0f, 4.0f));
}

void UTenFeEquipmentMenuWidget::RefreshSummary()
{
    if (!Character || !SummaryText)
    {
        return;
    }

    const UTenFeEquipmentComponent* Equipment = Character->GetEquipment();
    const FTenFeItemDefinition Weapon = Equipment->GetEquippedWeapon();
    SummaryText->SetText(FText::FromString(FString::Printf(
        TEXT("Equipada: %s\nDaño %.0f    Defensa %.0f    Peso total %.1f"),
        *Weapon.DisplayName.ToString(), Weapon.Damage, Equipment->GetTotalDefense(), Equipment->GetEquipmentWeight())));
}

void UTenFeEquipmentMenuWidget::SelectWeapon0() { if (Character) Character->GetEquipment()->EquipWeapon(0); }
void UTenFeEquipmentMenuWidget::SelectWeapon1() { if (Character) Character->GetEquipment()->EquipWeapon(1); }
void UTenFeEquipmentMenuWidget::SelectWeapon2() { if (Character) Character->GetEquipment()->EquipWeapon(2); }
void UTenFeEquipmentMenuWidget::EquipArmor0() { if (Character) Character->GetEquipment()->EquipArmor(0); }
void UTenFeEquipmentMenuWidget::EquipArmor1() { if (Character) Character->GetEquipment()->EquipArmor(1); }
void UTenFeEquipmentMenuWidget::EquipArmor2() { if (Character) Character->GetEquipment()->EquipArmor(2); }
void UTenFeEquipmentMenuWidget::CloseMenu() { if (Character) Character->ToggleEquipmentMenu(); }
